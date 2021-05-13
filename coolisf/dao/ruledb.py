# -*- coding: utf-8 -*-

"""
Rule DB for Optimus Engine
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import os.path
import logging

from texttaglib.puchikarui import with_ctx

from coolisf.dao import CorpusDAOSQLite
from coolisf.model import LexUnit, RuleInfo, PredInfo, RulePred, Reading


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

logger = logging.getLogger(__name__)
MY_DIR = os.path.dirname(os.path.realpath(__file__))
RULEDB_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'init_ruledb.sql')


def getLogger():
    return logging.getLogger(__name__)


class LexRuleDB(CorpusDAOSQLite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_file(RULEDB_INIT_SCRIPT)
        self.add_table('lexunit', ['ID', 'lemma', 'pos', 'synsetid', 'sentid', 'flag'], proto=LexUnit, id_cols=('ID',))
        self.add_table('ruleinfo', ['ID', 'head', 'lid', 'rid', 'flag'], proto=RuleInfo, id_cols=('ID',))
        self.add_table('rulepred', ['ruleid', 'predid', 'carg'], proto=RulePred)
        self.add_table('predinfo', ['ID', 'pred', 'predtype', 'lemma', 'pos', 'sense'], id_cols=('ID',), proto=PredInfo)

    def get_lexunit(self, lexunit, mode=None, ctx=None):
        lexunit.parses = self.get_sent(lexunit.sentid, mode=mode, ctx=ctx)
        return lexunit

    def flag(self, lexunit, flag, ctx):
        lexunit.flag = flag
        ctx.lexunit.save(lexunit, columns=('flag',))

    @with_ctx
    def find_lexunits(self, lemma=None, pos=None, flag=None, limit=None, lazy=False, ctx=None):
        query = []
        params = []
        if lemma:
            query.append("lemma = ?")
            params.append(lemma)
        if pos:
            query.append("pos = ?")
            params.append(pos)
        if flag:
            query.append("flag = ?")
            params.append(flag)
        lexunits = ctx.lexunit.select(" AND ".join(query), params, limit=limit)
        if lazy:
            for lu in lexunits:
                lu.parses = self.get_sent(lu.sentid, ctx=ctx)
        return lexunits

    @with_ctx
    def generate_rules(self, lexunits, parser=None, ctx=None):
        # parse lexical units and save the parses
        for lu in lexunits:
            getLogger().debug("gererate_rules() lu -> {}".format(lu))
            lu.ID = ctx.lexunit.save(lu)
            self.parse_rule(lu, parser, ctx=ctx)

    doc_map = {'v': 'verb', 'n': 'noun', 'a': 'adj', 'r': 'adv', 'x': 'other'}

    @with_ctx
    def parse_rule(self, lu, parser=None, ctx=None):
        if parser is not None:
            parser(lu)
            if lu.parses is not None and len(lu.parses) > 0:
                if lu.pos in self.doc_map:
                    lu.parses.docID = self.get_doc(self.doc_map[lu.pos], ctx=ctx).ID
                else:
                    lu.parses.docID = self.get_doc("processed", ctx=ctx).ID
                self.save_sent(lu.parses, ctx=ctx)
                # save sentid, flag as processed
                lu.sentid = lu.parses.ID
                lu.flag = LexUnit.PROCESSED
                ctx.lexunit.save(lu, columns=('sentid', 'flag'))
                # link rulepred
                self.generate_ruleinfo(lu, ctx=ctx)
            else:
                lu.flag = LexUnit.ERROR
                ctx.lexunit.save(lu, columns=('flag',))

    @with_ctx
    def generate_ruleinfo(self, lu, ctx=None):
        for r in lu.parses:
            getLogger().debug("Adding rule {} -> {}".format(lu.lemma, r.dmrs()))
            head = r.dmrs().layout.head()
            if head is not None:
                rinfo = RuleInfo(lid=lu.ID, rid=r.ID, head=head.predstr)
                rinfo.ID = ctx.ruleinfo.save(rinfo)
                self.generate_rulepred(rinfo, reading=r, ctx=ctx)
                getLogger().info("Added {}".format(lu.lemma))
            else:
                getLogger().info("no head for {}, skipped".format(lu.lemma))

    @with_ctx
    def generate_rulepred(self, ruleinfo, reading=None, ctx=None):
        if not reading:
            reading = self.get_reading(Reading(ID=ruleinfo.rid), ctx=ctx)
        # save pred
        for node in reading.dmrs().layout.nodes:
            predinfo = ctx.predinfo.select_single('pred = ?', (str(node.pred),))
            if not predinfo:
                predinfo = PredInfo.from_string(str(node.pred))
                predinfo.ID = ctx.predinfo.save(predinfo)
            rid = ruleinfo.ID
            pid = predinfo.ID
            carg = node.carg
            rulepred = ctx.rulepred.select_single('ruleid=? AND predid=? AND carg=?', (rid, pid, carg))
            if not rulepred:
                rulepred = RulePred(ruleid=rid, predid=pid, carg=carg)
                ctx.rulepred.save(rulepred)

    @with_ctx
    def get_rule(self, lid, rid, ctx=None):
        lu = ctx.lexunit.by_id(lid)
        if lu is None:
            return None
        lu.parses = self.get_sent(lu.sentid, readingIDs=(rid,), ctx=ctx)
        if not len(lu.parses):
            return None
        return lu

    @with_ctx
    def flag_rule(self, lid, rid, flag, ctx=None):
        ctx.ruleinfo.update((flag,), 'lid=? AND rid=?', (lid, rid), ('flag',))

    @with_ctx
    def find_ruleinfo_by_head(self, head, carg=None, flag=None, ctx=None, restricted=True):
        """ Find rules related to a predicate """
        query = ['head = ?']
        params = [head]
        if restricted:
            query.append('lid IN (SELECT lid FROM lexunit WHERE flag > 3)')
        if flag is not None:
            query.append('flag = ?')
            params.append(flag)
        return ctx.ruleinfo.select(' AND '.join(query), params)

    @with_ctx
    def find_ruleinfo(self, nodes, restricted=True, limit=None, ctx=None):
        """ Find applicable rules for given DMRS nodes """
        template = """
head IN ({head}) {res}
AND (ID IN (SELECT ruleid FROM rulepred WHERE {incl})
     {incl_carg})
{excl_carg}
AND ID NOT IN (SELECT ruleid FROM rulepred WHERE {excl})
"""
        params_heads = ['udef_q', 'unknown']
        # ruleinfo's flag == 2 (coolisf.model.RuleInfo.COMPOUND)
        # lexunit.flag > 3
        restricted = 'AND flag = 2 AND lid IN (SELECT lid FROM lexunit WHERE flag > 3)' if restricted else ''
        params_nocargs = ['udef_q', 'unknown']
        cargs = set()
        params_cargs = []
        incl_carg_filters = []
        # excl_carg_filters = []
        for node in nodes:
            pred_str = str(node.pred)
            params_heads.append(pred_str)
            if node.carg:
                incl_carg_filters.append('(predid=(SELECT ID FROM predinfo WHERE pred=?) AND carg=?)')
                # excl_carg_filters.append('(predid=(SELECT ID FROM predinfo WHERE pred=?) AND carg=?)')
                params_cargs.extend((pred_str, node.carg))
                cargs.add(node.carg)
            else:
                params_nocargs.append(pred_str)
        # incl_carg_filters
        if incl_carg_filters:
            incl_carg = ' OR (ID IN (SELECT ruleid FROM rulepred WHERE {}))'.format('\n OR '.join(incl_carg_filters))
        else:
            incl_carg = ''
        if cargs:
            excl_carg_vars = ','.join(['?'] * len(cargs))
            excl_carg = ' AND ID NOT IN (SELECT ruleid FROM rulepred WHERE carg NOT IN ({}))'.format(excl_carg_vars)
        else:
            excl_carg = ''
        # if excl_carg_filters:
        #     excl_carg = 'AND ID NOT IN (SELECT ruleid FROM rulepred WHERE NOT ({}))'.format('\n OR '.join(excl_carg_filters))
        # else:
        #     excl_carg = ''
        nocarg_vars = ','.join(['?'] * (len(params_nocargs)))
        incl = 'predid IN (SELECT ID FROM predinfo WHERE pred IN ({}))'.format(nocarg_vars)
        heads_vars = ','.join(['?'] * (len(params_heads)))
        excl = 'predid NOT IN (SELECT ID FROM predinfo WHERE pred IN ({}))'.format(heads_vars)
        # exclude
        where = template.format(head=heads_vars,
                                res=restricted,
                                incl=incl,
                                incl_carg=incl_carg,
                                excl_carg=excl_carg,
                                excl=excl)
        params = params_heads + params_nocargs + params_cargs + list(cargs) + params_heads
        getLogger().debug("params_heads [{}] = {}".format(len(params_heads), params_heads))
        getLogger().debug("params_nocargs [{}] = {}".format(len(params_nocargs), params_nocargs))
        getLogger().debug("params_cargs [{}] = {}".format(len(params_cargs), params_cargs))
        getLogger().debug("where -> {}".format(where))
        return ctx.ruleinfo.select(where, params, columns=('ID', 'lid', 'rid'), limit=limit)


def parse_lexunit(lu, ERG):
    getLogger().debug("parse_lexunit() lu -> {}".format(lu))
    lu.parses = []
    if lu.pos == 'v':
        lu.parses = ERG.parse(lu.lemma, parse_count=20, extra_args=['-r', 'root_wn_v'])
    elif lu.pos == 'n':
        lu.parses = ERG.parse(lu.lemma, parse_count=20, extra_args=['-r', 'root_wn_n'])
    elif lu.pos in ('a', 's'):
        lu.parses = ERG.parse(lu.lemma, parse_count=20, extra_args=['-r', 'root_wn_adj'])
    elif lu.pos in ('r'):
        lu.parses = ERG.parse(lu.lemma, parse_count=20, extra_args=['-r', 'root_wn_adv'])
    if len(lu.parses) == 0:
        lu.parses = ERG.parse(lu.lemma, parse_count=20, extra_args=['-r', 'root_frag'])
    return lu
