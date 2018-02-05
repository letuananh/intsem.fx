# -*- coding: utf-8 -*-

'''
Rule DB for Optimus Engine
@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

########################################################################

import os
import os.path
import logging

from puchikarui import with_ctx

from coolisf.dao import CorpusDAOSQLite
from coolisf.model import LexUnit, RuleInfo


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

logger = logging.getLogger(__name__)
MY_DIR = os.path.dirname(os.path.realpath(__file__))
RULEDB_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'init_ruledb.sql')


class LexRuleDB(CorpusDAOSQLite):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_file(RULEDB_INIT_SCRIPT)
        self.add_table('lexunit', ['ID', 'lemma', 'pos', 'synsetid', 'sentid', 'flag'], proto=LexUnit, id_cols=('ID',))
        self.add_table('ruleinfo', ['pred', 'lid', 'rid', 'flag'], proto=RuleInfo)

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
            else:
                lu.flag = LexUnit.ERROR
                ctx.lexunit.save(lu, columns=('flag',))

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
    def find_rule(self, predstr, flag=None, ctx=None, restricted=True):
        query = ['pred = ?']
        params = [predstr]
        if restricted:
            query.append('lid IN (SELECT lid FROM lexunit WHERE flag > 3)')
        if flag is not None:
            query.append('flag = ?')
            params.append(flag)
        return ctx.ruleinfo.select(' AND '.join(query), params)


def parse_lexunit(lu, ERG):
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
