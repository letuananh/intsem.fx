#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Utility functions

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
import importlib
import threading
from collections import namedtuple
from delphin.interfaces import ace
from delphin.mrs.components import Pred

from chirptext import Counter, FileHelper
from puchikarui import Schema

from .shallow import JapaneseAnalyser, EnglishAnalyser
from .model import Sentence

try:
    from chirptext.deko import wakati
except:
    logging.warning('chirptext.deko cannot be imported. JNLP mode is disabled')

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


PrepInfo = namedtuple("PrepInfo", ["module_name", "class_name"])


class PrepManager(object):

    def __init__(self):
        self.prep_canon_map = {}  # map (module, cls) to an actual prep object
        self.name_map = {}  # map a friendly name to a prep object

    def register(self, friendly_name, module_name, class_name):
        self.name_map[friendly_name] = PrepInfo(module_name, class_name)

    def build_prep(self, prep_info, prep_name=""):
        ''' Build or retrieve a preprocessor object based on its specs '''
        if prep_info not in self.prep_canon_map:
            with threading.Lock():
                module = importlib.import_module(prep_info.module_name)
                cls = getattr(module, prep_info.class_name)
                prep = cls(prep_info, prep_name)
                self.prep_canon_map[prep_info] = prep
        return self.prep_canon_map[prep_info]

    def __getitem__(self, prep_name):
        if prep_name not in self.name_map:
            raise LookupError("Invalid prep_name ({} was provided)".format(prep_name))
        prep_info = self.name_map[prep_name]
        return self.build_prep(prep_info, prep_name)

    @staticmethod
    def from_json(json_data):
        man = PrepManager()
        for k, info in json_data.items():
            man.register(k, info["module"], info["class"])
        return man


class Preprocessor(object):
    ''' Standard preprocessor structure '''

    def __init__(self, info, name=""):
        self.info = info
        self.name = name

    def process(self, text):
        return text


class PrepDeko(Preprocessor):

    def __init__(self, info, name="deko"):
        super().__init__(info, name)
        self.parser = JapaneseAnalyser()

    def process(self, sent):
        if isinstance(sent, Sentence):
            sent.shallow = self.parser.analyse(sent.text)
            sent.text = ' '.join(t.label for t in sent.shallow.tokens)
            return sent
        else:
            return self.process(Sentence(sent))


class PrepNLTK(Preprocessor):

    def __init__(self, info, name="nltk"):
        super().__init__(info, name)
        self.parser = EnglishAnalyser()

    def process(self, sent):
        if isinstance(sent, Sentence):
            sent.shallow = self.parser.analyse(sent.text)
            sent.text = ' '.join(t.label for t in sent.shallow.tokens)
            return sent
        else:
            return self.process(Sentence(sent))


class PrepMeCab(Preprocessor):

    def __init__(self, info, name="mecab"):
        super().__init__(info, name)

    def process(self, sent):
        if isinstance(sent, Sentence):
            sent.text = wakati(sent.text)
            return sent
        else:
            return wakati(sent)


def read_ace_output(ace_output_file):
    ''' Read output file from ACE batch mode
    Sample command: ace -g grammar.dat infile.txt > outfile.txt
    Read more: http://moin.delph-in.net/AceOptions
    '''
    logger.info("Reading parsed MRS from %s..." % (ace_output_file,))
    c = Counter()
    items = []
    sentences = []
    skipped = []
    with open(ace_output_file, 'r') as input_mrs:
        current_sid = 0
        while True:
            current_sid += 1
            line = input_mrs.readline()
            if line.startswith('SENT'):
                mrs_line = input_mrs.readline()
                # item = [line, mrs_line]
                s = Sentence(line[5:], sid=current_sid)
                sentences.append(s)
                while mrs_line.strip():
                    s.add(mrs_line)
                    mrs_line = input_mrs.readline()
                input_mrs.readline()
                c.count('sent')
                c.count('total')
            elif line.startswith('SKIP'):
                skipped.append(line[5:].strip())
                items.append([line])
                input_mrs.readline()
                input_mrs.readline()
                c.count('skip')
                c.count('total')
            else:
                break
    c.summarise()
    FileHelper.save(ace_output_file + '.skipped.txt', '\n'.join(skipped))
    return sentences


def sent2json(sent, sentence_text=None, parse_count=-1, tagger='N/A', grammar='N/A'):
    xml_str = sent.to_visko_xml_str()
    sent_json = {'sent': sentence_text if sentence_text else sent.text,
                 'parse_count': parse_count,
                 'tagger': tagger,
                 'grammar': grammar,
                 'parses': [parse2json(x) for x in sent],
                 'xml': xml_str,
                 'latex': sent.to_latex(),
                 'shallow': sent.shallow.to_json() if sent.shallow else {}}
    if sent.flag is not None:
        sent_json['flag'] = sent.flag
    if sent.comment is not None:
        sent_json['comment'] = sent.comment
    return sent_json


def parse2json(parse):
    return {'pid': parse.ID,
            'ident': parse.ident,
            'mrs': parse.mrs().json(),
            'dmrs': parse.dmrs().json(),
            'mrs_raw': parse.mrs().tostring(),
            'dmrs_raw': parse.dmrs().tostring()}


class AceCache(Schema):

    def __init__(self, data_source, setup_script=None, setup_file=AC_INIT_SCRIPT):
        Schema.__init__(self, data_source, setup_script=setup_script, setup_file=setup_file)
        self.add_table('sent', ['ID', 'text', 'grm', 'pc'])
        self.add_table('mrs', ['ID', 'sid', 'mrs'])

    def save(self, sent, grm, pc):
        if pc is None:
            self.sent.delete("text=? AND grm=? AND pc IS NULL", (sent.text, grm))
        else:
            self.sent.delete("text=? AND grm=? AND pc=?", (sent.text, grm, pc))
        sid = self.sent.insert(sent.text, grm, pc)
        for p in sent:
            self.mrs.insert(sid, p.mrs()._raw)

    def load(self, sent, grm, pc):
        if pc is None:
            sobj = self.sent.select_single('text=? AND grm=? AND pc IS NULL', (sent, grm))
        else:
            sobj = self.sent.select_single('text=? AND grm=? AND pc=?', (sent, grm, pc))
        if not sobj:
            return None
        else:
            s = Sentence(sobj.text)
            parses = self.mrs.select('sid=?', (sobj.ID,))
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
        sid = self.sent.insert(txt, grammar, pc, tagger, sent.text, sent.to_visko_xml_str(), sent.to_latex(), json.dumps(sent.shallow.to_json()) if sent.shallow else None)
        for p in sent:
            # insert parses
            self.parse.insert(sid, p.ID, p.ident, p.mrs().json_str(), p.dmrs().json_str(), p.mrs().tostring(), p.dmrs().tostring())

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
        self.preps = PrepManager.from_json(self.cfg["preprocessors"])

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
            self.grammars[grm] = Grammar(grm, ginfo['path'], ginfo['args'], ace_bin, cache_loc, preps)
        # done creating grammar
        return self.grammars[grm]

    def lookup_preps(self, gcfg):
        if 'preps' not in gcfg:
            return None
        else:
            return [self.preps[pname] for pname in gcfg['preps']]

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
    def __init__(self, name, gram_file, cmdargs, ace_bin, cache_loc, preps=None):
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
        self.preps = preps

    def parse(self, text, parse_count=None, ignore_cache=False):
        if not ignore_cache and self.cache:
            # try to fetch from cache first
            s = self.cache.load(text, self.name, parse_count)
            if s:
                logger.debug("Retrieved {pc} parses from cache for sent: {s}".format(s=text, pc=len(s.parses)))
                return s
        s = Sentence(text)
        args = self.cmdargs
        if parse_count:
            args += ['-n', str(parse_count)]
        with ace.AceParser(self.gram_file, executable=self.ace_bin, cmdargs=args) as parser:
            # preprocessor
            if self.preps:
                for prep in self.preps:
                    input_text = prep.process(s)
            result = parser.interact(s.text)
        if result and 'RESULTS' in result:
            top_res = result['RESULTS']
            for mrs in top_res:
                s.add(mrs['MRS'])
        # cache it
        if self.cache:
            self.cache.save(s, self.name, parse_count)
        return s


def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
