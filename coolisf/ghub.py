# -*- coding: utf-8 -*-

'''
Grammar helpers

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    ACE:
        http://moin.delph-in.net/AceOptions
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import logging
import json
from delphin.interfaces import ace

from puchikarui import Schema
from chirptext import FileHelper

from coolisf.util import sent2json
from coolisf.model import Sentence
from coolisf.processors.base import ProcessorManager



##########################################
# CONFIGURATION
##########################################

MY_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(MY_DIR, 'config.json')
PC_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'initpc.sql')
AC_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'initac.sql')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


########################################################################

class AceCache(Schema):

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

    def clear(self, text, grm, pc, extra_args, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.clear(text, grm, pc, extra_args, ctx=ctx)
        # now there is ctx
        query, params = self.build_query(text, grm, pc, extra_args)
        ctx.sent.delete(' AND '.join(query), params)

    def save(self, sent, grm, pc, extra_args, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.save(sent, grm, pc, extra_args, ctx=ctx)
        self.clear(sent.text, grm, pc, extra_args, ctx=ctx)
        sid = ctx.sent.insert(sent.text, grm, pc, extra_args)
        for p in sent:
            ctx.mrs.insert(sid, p.mrs()._raw)

    def load(self, text, grm, pc, extra_args, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.load(text, grm, pc, extra_args, ctx=ctx)
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

    def save(self, txt, grammar, pc, tagger, sent):
        # delete old data
        # dq, dp = self.build_query(sent.text, grammar, pc, tagger)
        # self.sent.delete(dq, dp)
        # TODO: delete parses as well ...
        sid = self.sent.insert(txt, grammar, pc, tagger, sent.text, sent.to_xml_str(), sent.to_latex(), json.dumps(sent.shallow.to_json()) if sent.shallow else None)
        for r in sent:
            # insert parses
            self.parse.insert(sid, r.ID, r.rid, r.mrs().json_str(), r.dmrs().json_str(), r.mrs().tostring(), r.dmrs().tostring())

    def load(self, txt, grm, pc, tagger):
        query, params = self.build_query(txt, grm, pc, tagger)
        sobj = self.sent.select_single(query, params)
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
        parses = self.parse.select('sid=?', (sobj.ID,))
        for p in parses:
            sent['parses'].append({'pid': p.pid,
                                   'ident': p.ident,
                                   'mrs': json.loads(p.jmrs),
                                   'dmrs': json.loads(p.jdmrs),
                                   'mrs_raw': p.mrs,
                                   'dmrs_raw': p.dmrs})
        return sent


class GrammarHub:

    def __init__(self, cfg_path=CONFIG_FILE):
        self.read_config(cfg_path)
        self.grammars = {}
        if self.cache_path:
            self.cache = ISFCache(self.cache_path)
        else:
            self.cache = None
        self.preps = ProcessorManager.from_json(self.cfg["preprocessors"])
        self.posts = ProcessorManager.from_json(self.cfg["postprocessors"])

    def read_config(self, cfg_path=CONFIG_FILE):
        logger.info("Reading grammars configuration from: {}".format(cfg_path))
        with open(cfg_path) as cfgfile:
            self.cfg = json.loads(cfgfile.read())
            self.cache_path = FileHelper.abspath(self.cfg['cache'])
            logger.info("ISF Cache DB: {o} => {c}".format(o=self.cfg['cache'], c=self.cache_path))
        return self.cfg

    @property
    def names(self):
        return tuple(self.cfg['grammars'].keys())

    @property
    def available(self):
        ''' Available grammars and their friendly names '''
        return {k: g['name'] for k, g in self.cfg['grammars'].items()}

    def __getattr__(self, name):
        return self.get_grammar(name)

    def __getitem__(self, grm):
        return self.get_grammar(grm)

    def get_grammar(self, grm):
        if grm not in self.cfg['grammars']:
            raise LookupError("Unknown grammar ({})".format(grm))
        if grm not in self.grammars:
            ginfo = self.cfg['grammars'][grm]
            ace_bin = ginfo['ace'] if 'ace' in ginfo else self.cfg['ace']
            cache_loc = ginfo['acecache'] if 'acecache' in ginfo else self.cfg['acecache'] if 'acecache' in self.cfg else None
            preps = self.lookup_preps(ginfo)
            posts = self.lookup_posts(ginfo)
            self.grammars[grm] = Grammar(grm, ginfo['path'], ginfo['args'], ace_bin, cache_loc, preps=preps, posts=posts)
        # done creating grammar
        return self.grammars[grm]

    def lookup_preps(self, gcfg):
        if 'preps' not in gcfg:
            return None
        else:
            return [self.preps[pname] for pname in gcfg['preps']]

    def lookup_posts(self, gcfg):
        if 'posts' not in gcfg:
            return None
        else:
            return [self.posts[pname] for pname in gcfg['posts']]

    def parse_json(self, txt, grm, pc=None, tagger=None, ignore_cache=False):
        # validation
        if not txt:
            raise ValueError('Sentence cannot be empty')
        # look up from cache first
        if not ignore_cache and self.cache:
            s = self.cache.load(txt, grm, pc, tagger)
            if s is not None:
                logger.info("Retrieved {} parse(s) from cache for sent: {}".format(len(s['parses']), s['sent']))
                return s
        # else parse it ...
        sent = self.parse(txt, grm, pc, tagger, ignore_cache)
        # cache sent if possible
        if self.cache:
            self.cache.save(txt, grm, pc, tagger, sent)
        # make it JSON
        return sent2json(sent, txt, pc, tagger, grm)

    def parse(self, txt, grm, pc=None, tagger=None, ignore_cache=False):
        ''' Parse a sentence using ISF '''
        # validation
        if not txt:
            raise ValueError('Sentence cannot be empty')
        # Parse sentence
        logger.debug("Parsing sentence: {}".format(txt))
        sent = self[grm].parse(txt, parse_count=pc)
        if tagger:
            logger.info("Sense-tagging sentence using {}".format(tagger))
            sent.tag(method=tagger)
        return sent


class Grammar:
    def __init__(self, name, gram_file, cmdargs, ace_bin, cache_loc, preps=None, posts=None):
        self.name = name
        self.gram_file = FileHelper.abspath(gram_file)
        self.cmdargs = cmdargs
        self.ace_bin = FileHelper.abspath(ace_bin)
        logger.info("Initializing grammar {n} | GRM Path: [{g}] - ACE: [{a}]".format(n=self.name, g=self.gram_file, a=self.ace_bin))
        # init cache
        if cache_loc:
            self.cache_loc = FileHelper.abspath(cache_loc)
            self.cache = AceCache(self.cache_loc)
            logger.info("Caching enabled for grammar [{g}] at [{l}]".format(g=self.name, l=self.cache_loc))
        else:
            self.cache = None
        self.preps = preps  # pre-processors
        self.posts = posts  # post-processors

    def generate(self, parse_obj):
        ''' Generate text from coolisf.model.Parse object '''
        with ace.AceGenerator(self.gram_file, executable=self.ace_bin) as generator:
            response = generator.interact(str(parse_obj.mrs()))
            sents = []
            if response and 'RESULTS' in response:
                for res in response['RESULTS']:
                    text = res['SENT']
                    mrs = res['MRS']
                    # tree: res['tree']
                    # deriv: res['DERIV']
                    sent = Sentence(text)
                    sent.add(mrs)
                    sents.append(sent)
            return sents

    def parse_many_iterative(self, texts, parse_count=None, extra_args=None, ignore_cache=None):
        args = self.cmdargs.copy()
        if parse_count:
            args += ['-n', str(parse_count)]
        if extra_args:
            args += extra_args
        with ace.AceParser(self.gram_file, executable=self.ace_bin, cmdargs=args) as parser, self.cache.ctx() as ctx:
            logger.debug("Executing ACE with cmdargs: {}".format(args))
            for text in texts:
                exargs_str = ' '.join(extra_args) if extra_args else None
                if not ignore_cache and self.cache:
                    # try to fetch from cache first
                    s = self.cache.load(text, self.name, parse_count, exargs_str, ctx=ctx)
                    if s is not None:
                        logger.debug("Retrieved {pc} parses from cache for sent: {s}".format(s=text, pc=len(s)))
                        yield s
                        continue
                # not in cache then ...
                s = Sentence(text)
                # preprocessor
                if self.preps:
                    for prep in self.preps:
                        prep.process(s)
                result = parser.interact(s.text)
                if result and 'RESULTS' in result:
                    top_res = result['RESULTS']
                    for mrs in top_res:
                        parse = s.add(mrs['MRS'])
                        if self.posts:
                            for p in self.posts:
                                p.process(parse)
                # cache it
                if self.cache:
                    self.cache.save(s, self.name, parse_count, exargs_str, ctx=ctx)
                yield s

    def parse_many(self, texts, parse_count=None, extra_args=None, ignore_cache=False):
        sents = []
        for sent in self.parse_many_iterative(texts, parse_count, extra_args, ignore_cache):
            sents.append(sent)
        return sents

    def parse(self, text, parse_count=None, extra_args=None, ignore_cache=False):
        return self.parse_many((text,), parse_count, extra_args, ignore_cache)[0]
