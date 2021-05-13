# -*- coding: utf-8 -*-

"""
Grammar helpers
"""

# See also:
# Ace: http://moin.delph-in.net/AceOptions
#
# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging
from delphin.interfaces import ace

from texttaglib.chirptext import FileHelper

from coolisf.config import read_config
from coolisf.dao.cache import AceCache, ISFCache
from coolisf.util import sent2json
from coolisf.model import Sentence
from coolisf.processors.base import ProcessorManager


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


########################################################################

class GrammarHub:

    def __init__(self):
        self.read_config()
        self.grammars = {}
        if self.cache_path:
            self.cache = ISFCache(self.cache_path)
        else:
            self.cache = None
        self.preps = ProcessorManager.from_json(self.cfg["preprocessors"])
        self.posts = ProcessorManager.from_json(self.cfg["postprocessors"])

    def read_config(self):
        self.cfg = read_config()
        if not self.cfg:
            raise Exception("Application configuration could not be read")
        if 'cache' in self.cfg:
            self.cache_path = self.to_path(self.cfg['cache'])
        else:
            self.cache_path = None
        getLogger().info("ISF Cache DB: {o} => {c}".format(o=self.cfg['cache'], c=self.cache_path))
        return self.cfg

    def to_path(self, path):
        return FileHelper.abspath(path.format(data_root=self.cfg['data_root']))

    @property
    def names(self):
        return tuple(self.cfg['grammars'].keys())

    @property
    def available(self):
        """ Available grammars and their friendly names """
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
            if 'acecache' in ginfo:
                cache_loc = self.to_path(ginfo['acecache'])
            elif 'acecache' in self.cfg:
                cache_loc = self.to_path(self.cfg['acecache'])
            else:
                cache_loc = None
            preps = self.lookup_preps(ginfo)
            posts = self.lookup_posts(ginfo)
            grm_path = self.to_path(ginfo['path'])
            self.grammars[grm] = Grammar(grm, grm_path, ginfo['args'], ace_bin, cache_loc, preps=preps, posts=posts)
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
                getLogger().debug("Retrieved {} parse(s) from cache for sent: {}".format(len(s['parses']), s['sent']))
                return s
        # else parse it ...
        sent = self.parse(txt, grm, pc, tagger, ignore_cache)
        # cache sent if possible
        if self.cache and not ignore_cache:
            self.cache.save(txt, grm, pc, tagger, sent)
        # make it JSON
        return sent2json(sent, txt, pc, tagger, grm)

    def parse(self, txt, grm, pc=None, tagger=None, ignore_cache=False, wsd=None, ctx=None):
        """ Parse a sentence using ISF """
        # validation
        if not txt:
            raise ValueError('Sentence cannot be empty')
        # Parse sentence
        getLogger().debug("Parsing sentence: {}".format(txt))
        sent = self[grm].parse(txt, parse_count=pc, ignore_cache=ignore_cache)
        if tagger:
            getLogger().debug("Sense-tagging sentence using {}".format(tagger))
            sent.tag_xml(method=tagger, wsd=wsd, ctx=ctx)
        return sent


class Grammar:
    def __init__(self, name, gram_file, cmdargs, ace_bin, cache_loc, preps=None, posts=None):
        self.name = name
        self.gram_file = FileHelper.abspath(gram_file)
        self.cmdargs = cmdargs
        self.ace_bin = FileHelper.abspath(ace_bin)
        getLogger().debug("Initializing grammar {n} | GRM Path: [{g}] - ACE: [{a}]".format(n=self.name, g=self.gram_file, a=self.ace_bin))
        # init cache
        if cache_loc:
            self.cache_loc = FileHelper.abspath(cache_loc)
            self.cache = AceCache(self.cache_loc)
            getLogger().debug("Caching enabled for grammar [{g}] at [{l}]".format(g=self.name, l=self.cache_loc))
        else:
            self.cache = None
        self.preps = preps  # pre-processors
        self.posts = posts  # post-processors

    def generate(self, parse_obj):
        """ Generate text from coolisf.model.Parse object """
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
            getLogger().debug("Executing ACE with cmdargs: {}".format(args))
            for text in texts:
                exargs_str = ' '.join(extra_args) if extra_args else None
                if not ignore_cache and self.cache:
                    # try to fetch from cache first
                    s = self.cache.load(text, self.name, parse_count, exargs_str, ctx=ctx)
                    if s is not None:
                        getLogger().debug("Retrieved {pc} parses from cache for sent: {s}".format(s=text, pc=len(s)))
                        yield s
                        continue
                # not in cache then ...
                s = Sentence(text)
                try:
                    # preprocessors
                    if self.preps:
                        for prep in self.preps:
                            prep.process(s)
                    # interact with grammar
                    getLogger().debug("interacting with ACE")
                    result = parser.interact(s.text)
                    getLogger().debug("reading ACE output")
                    # postprocessors
                    if result and 'RESULTS' in result:
                        top_res = result['RESULTS']
                        for mrs in top_res:
                            parse = s.add(mrs['MRS'])
                            if self.posts:
                                for p in self.posts:
                                    p.process(parse)
                    # cache it
                    if not ignore_cache and self.cache:
                        getLogger().debug("Caching result")
                        self.cache.save(s, self.name, parse_count, exargs_str, ctx=ctx)
                except Exception as e:
                    s.flag = Sentence.ERROR
                    s.comment = "This sentence is not fully processed"
                    getLogger().exception("Error happened while processing sentence: {}".format(text))
                yield s

    def parse_many(self, texts, parse_count=None, extra_args=None, ignore_cache=False):
        sents = []
        for sent in self.parse_many_iterative(texts, parse_count, extra_args, ignore_cache):
            sents.append(sent)
        return sents

    def parse(self, text, parse_count=None, extra_args=None, ignore_cache=False):
        return self.parse_many((text,), parse_count, extra_args, ignore_cache)[0]
