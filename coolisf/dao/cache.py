# -*- coding: utf-8 -*-

"""
Cache DAO - Caching ACE and ISF parse results
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import os.path
import logging
import json

from texttaglib.puchikarui import Schema, with_ctx

from coolisf.model import Sentence


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

logger = logging.getLogger(__name__)
MY_DIR = os.path.dirname(os.path.realpath(__file__))
PC_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'init_isf_cache.sql')
AC_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'init_ace_cache.sql')


class AceCache(Schema):
    """ Cache ACE output """

    def __init__(self, data_source, setup_script=None, setup_file=AC_INIT_SCRIPT):
        Schema.__init__(self, data_source, setup_script=setup_script, setup_file=setup_file)
        self.add_table('sent', ['ID', 'text', 'grm', 'pc', 'extra_args'])
        self.add_table('mrs', ['ID', 'sid', 'mrs'])

    def build_query(self, text, grm, pc, extra_args):
        query = ['text = ?', 'grm = ?']
        params = [text, grm]
        if pc is None:
            query.append('pc IS NULL')
        else:
            query.append('pc = ?')
            params.append(pc)
        if extra_args is None:
            query.append('extra_args IS NULL')
        else:
            query.append('extra_args = ?')
            params.append(extra_args)
        return query, params

    @with_ctx
    def clear(self, text, grm, pc, extra_args, ctx=None):
        query, params = self.build_query(text, grm, pc, extra_args)
        ctx.sent.delete(' AND '.join(query), params)

    @with_ctx
    def save(self, sent, grm, pc, extra_args, ctx=None):
        self.clear(sent.text, grm, pc, extra_args, ctx=ctx)
        sid = ctx.sent.insert(sent.text, grm, pc, extra_args)
        # store MRS
        for p in sent:
            ctx.mrs.insert(sid, p.mrs()._raw)
        # store shallow
        # store tags?

    @with_ctx
    def load(self, text, grm, pc, extra_args, ctx=None):
        query, params = self.build_query(text, grm, pc, extra_args)
        sobj = ctx.sent.select_single(' AND '.join(query), params)
        if not sobj:
            return None
        else:
            s = Sentence(sobj.text)
            parses = ctx.mrs.select('sid=?', (sobj.ID,))
            for p in parses:
                s.add(p.mrs)
            return s


class ISFCache(Schema):
    """ Cache ISF output """

    def __init__(self, data_source, setup_script=None, setup_file=PC_INIT_SCRIPT):
        Schema.__init__(self, data_source, setup_script=setup_script, setup_file=setup_file)
        self.add_table('sent', ['ID', 'raw', 'grm', 'pc', 'tagger', 'text', 'xml', 'latex', 'shallow'])
        self.add_table('parse', ['ID', 'sid', 'pid', 'ident', 'jmrs', 'jdmrs', 'mrs', 'dmrs'])

    def build_query(self, txt, grammar, pc, tagger):
        q = 'raw=? AND grm=?'
        p = [txt, grammar]
        if tagger is None:
            q += ' AND tagger IS NULL'
        else:
            q += ' AND tagger=?'
            p.append(tagger)
        if pc is None:
            q += ' AND pc IS NULL'
        else:
            q += ' AND pc=?'
            p.append(pc)
        return (q, p)

    @with_ctx
    def save(self, txt, grammar, pc, tagger, sent, ctx=None):
        # delete old data
        # dq, dp = self.build_query(sent.text, grammar, pc, tagger)
        # self.sent.delete(dq, dp)
        # TODO: delete parses as well ...
        sid = ctx.sent.insert(txt, grammar, pc, tagger, sent.text, sent.to_xml_str(), sent.to_latex(), json.dumps(sent.shallow.to_json()) if sent.shallow else None)
        for r in sent:
            # insert parses
            ctx.parse.insert(sid, r.ID, r.rid, r.mrs().json_str(), r.dmrs().json_str(), r.mrs().tostring(), r.dmrs().tostring())

    @with_ctx
    def load(self, txt, grm, pc, tagger, ctx=None):
        query, params = self.build_query(txt, grm, pc, tagger)
        sobj = ctx.sent.select_single(query, params)
        # logger.debug("q", query, "p", params, "sobj", sobj)
        if not sobj:
            return None
        # else
        sent = {'sent': sobj.text,
                'parse_count': sobj.pc,
                'tagger': sobj.tagger,
                'grammar': sobj.grm,
                'parses': [],
                'xml': sobj.xml,
                'latex': sobj.latex,
                'shallow': json.loads(sobj.shallow) if sobj.shallow else None}
        # select parses
        parses = ctx.parse.select('sid=?', (sobj.ID,))
        for p in parses:
            sent['parses'].append({'pid': p.pid,
                                   'ident': p.ident,
                                   'mrs': json.loads(p.jmrs),
                                   'dmrs': json.loads(p.jdmrs),
                                   'mrs_raw': p.mrs,
                                   'dmrs_raw': p.dmrs})
        return sent
