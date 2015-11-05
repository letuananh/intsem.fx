#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Extracting MWE from ERG's lexicon

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import codecs
import re
from collections import namedtuple
from collections import defaultdict
import xml.etree.ElementTree as ET
import xml.dom.minidom
import csv

from delphin.interfaces import ace
from delphin.mrs.components import Pred

from chirptext.leutile import StringTool
from chirptext.leutile import Counter
from chirptext.leutile import FileTool
from chirptext.leutile import TextReport
from chirptext.leutile import FileHub
from chirptext.leutile import Timer
from chirptext.texttaglib import writelines

from lelesk import LeLeskWSD # WSDResources
from lelesk.config import LLConfig

from .model import Sentence
from .util import PredSense

########################################################################

MWE_NOTFOUND = os.path.expanduser('data/mwe_notfound.txt')
MWE_FOUND = os.path.expanduser('data/mwe_found.txt')
MWE_PRED_LEMMA = os.path.expanduser('data/mwe_pred_lemma.txt')
LEXDB = os.path.expanduser('data/lexdb.rev')
ERG_PRED_FILE = FileTool.abspath('data/ergpreds.py')
ERG_PRED_FILE_TEMPLATE = open(FileTool.abspath('data/ergpreds.template.py'),'r').read()

ERGLexTup = namedtuple('ERGLex', 'name userid modstamp dead lextype orthography keyrel altkey alt2key keytag altkeytag compkey ocompkey pronunciation complete semclasses preferences classifier selectrest jlink comments exemplars usages lang country dialect domains genres register confidence source'.split())

class ERGLex:
    
    def __init__(self, name, userid, modstamp, dead, lextype, orthography, keyrel, altkey, alt2key, keytag, altkeytag, compkey, ocompkey, pronunciation, complete, semclasses, preferences, 
                classifier, selectrest, jlink, comments, exemplars, usages, lang, country, dialect, domains, genres, register, confidence, source):
        # user defined
        # LexDbFieldMappings >>> HOW TO create initial .fld file (first 4 columns are name, userid, modstamp, dead)
        self.name          = name
        self.userid        = userid
        self.modstamp      = modstamp
        self.dead          = (False if dead == 'f' else True)
        # the rest in lexdb.fld
        self.lextype       = lextype
        self.orthography   = orthography
        self.keyrel        = keyrel
        self.altkey        = altkey
        self.alt2key       = alt2key
        self.keytag        = keytag
        self.altkeytag     = altkeytag
        self.compkey       = compkey
        self.ocompkey      = ocompkey
        self.pronunciation = pronunciation
        self.complete      = complete
        self.semclasses    = semclasses
        self.preferences   = preferences
        self.classifier    = classifier
        self.selectrest    = selectrest
        self.jlink         = jlink
        self.comments      = comments
        self.exemplars     = exemplars
        self.usages        = usages 
        self.lang          = lang 
        self.country       = country
        self.dialect       = dialect
        self.domains       = domains
        self.genres        = genres
        self.register      = register
        self.confidence    = confidence
        self.source        = source
        
    def __str__(self):
        return "name = %s | userid = %s | modstamp = %s | dead = %s | lextype = %s | orthography = %s | keyrel = %s | altkey = %s | alt2key = %s | keytag = %s | altkeytag = %s | compkey = %s | ocompkey = %s | pronunciation = %s | complete = %s | semclasses = %s | preferences = %s | classifier = %s | selectrest = %s | jlink = %s | comments = %s | exemplars = %s | usages = %s | lang = %s | country = %s | dialect = %s | domains = %s | genres = %s | register = %s | confidence = %s | source = %s" % (self.name, self.userid, self.modstamp, self.dead, self.lextype, self.orthography, self.keyrel, self.altkey, self.alt2key, self.keytag, self.altkeytag, self.compkey, self.ocompkey, self.pronunciation, self.complete, self.semclasses, self.preferences, self.classifier, self.selectrest, self.jlink, self.comments, self.exemplars, self.usages, self.lang, self.country, self.dialect, self.domains, self.genres, self.register, self.confidence, self.source)
        
def to_sense_map(k,v):
    return '"%s" : [ %s ]' % (k,", ".join([ "SenseInfo('%s-%s', '%s', %s)" % (x.sid, x.pos, x.sk.replace("'", "\\'"), x.tagcount) for x in v ]))

def get_erg_lex():
    senses_map = defaultdict(list)
    c = Counter()

    with open(LEXDB, 'r') as lexdb:
        rows = list(csv.reader(lexdb, delimiter='\t'))
    return [ ERGLex(*row) for row in rows ]

def dev():
    # TODO: Something is wrong with _pass_v_along ...
    keyrels = [ "_give_v_off_rel", "give_v_off_rel", "_pass_v_along_rel", "pass_v_along_rel" ]
    for kr in keyrels:
        senses = PredSense.search_pred_string(kr)
        print("%s => %s" % (kr, senses))
    print("-" * 20)
    # return

    outfiles = FileHub('.txt')
    lexs  = get_erg_lex()
    c = Counter()
    lpsr_pattern = re.compile(r"_?[a-zA-Z0-9\-\+\\\/\$]+_[a-zA-Z]+_[0-9]+_rel") # _dog_n_1_rel
    lpr_pattern = re.compile(r"_?[a-zA-Z\-\+\\]+_[a-zA-Z]+_rel") # _dog_n_rel
    lr_pattern = re.compile(r"_?[a-zA-Z0-9\-\+\\]+_rel") # person_rel
    llr_pattern = re.compile(r"_?[a-zA-Z\-\+\\]+_[a-zA-Z\-\+\\]+_rel") # comp_not+so_rel
    lplr_pattern = re.compile(r"_?[a-zA-Z\-\+\\]+_[a-zA-Z]+_[a-zA-Z0-9\+\-]+_rel") # _abate_v_cause_rel
    for lex in lexs:
        if lex.keyrel == '\\N':
            c.count("\\N")
        elif lpsr_pattern.match(lex.keyrel):
            outfiles.writeline('data/ergpreds_lpsr', lex.keyrel)
            c.count("_lemma_pos_senseno_rel")
        elif lpr_pattern.match(lex.keyrel):
            outfiles.writeline('data/ergpreds_lpr', lex.keyrel)
            c.count("_lemma_pos_rel")
        elif lr_pattern.match(lex.keyrel):
            outfiles.writeline('data/ergpreds_lr', lex.keyrel)
            c.count("_lemma_rel")
        elif llr_pattern.match(lex.keyrel):
            outfiles.writeline('data/ergpreds_llr', lex.keyrel)
            c.count("_lemma_suplem_rel")
        elif lplr_pattern.match(lex.keyrel):
            outfiles.writeline('data/ergpreds_lplr', lex.keyrel)
            c.count("_lemma_pos_suplem_rel")
        else:
            outfiles.writeline('data/ergpreds_unknown', lex.keyrel)
            c.count("UNKNOWN")
    outfiles.close()
    c.summarise()
    print("-" * 20)

def extract_all_rel():
    # report header
    t = Timer()
    report = TextReport(ERG_PRED_FILE)
    senses_map = defaultdict(list)
    c = Counter()

    t.start("Extracting preds from ERG")
    lex_entries = get_erg_lex()
    t.end()

    t.start("Mapping those to wordnet senses")
    for lex in lex_entries:
        c.count('Entry')
        if lex.keyrel != '\\N':
            if not lex.keyrel.endswith('_rel'):
                c.count('WARNING')
                print(lex.keyrel)
            else:
                senses = PredSense.search_pred_string(lex.keyrel)
                senses_map[lex.keyrel] += senses
                # if lex.keyrel == '_pass_v_along_rel':
                #    print("%s => %s" % (lex.keyrel, senses))
    t.end()

    t.start("Saving predlinks to file")
    report.print(ERG_PRED_FILE_TEMPLATE)
    report.print("ERG_PRED_MAP = {")
    senses_list = [ to_sense_map(k,v) for k,v in senses_map.items() ] 
    report.print(",\n".join(senses_list))
    report.print("}")
    c.summarise()
    report.close()
    t.end("Mapping info has been written to %s" % (ERG_PRED_FILE,))
    pass

def extract_mwe():
    print("Loading WordNet ...")
    all_senses = WSDResources.singleton(True).wnsql.all_senses()
    
    print("Extracting MWE from ERG's lexicon")
    erg = codecs.open(os.path.expanduser("~/logon/lingo/erg/lexicon.tdl"), 'r', encoding='utf-8')
    pvs = set()
    prt = set()
    mwe = None
    mwe_list = set()
    mwe_lemma_map = {}
    for l in erg:
        if ':=' in l:
            m = re.match(r"([a-z_]+)_v[0-9]+ := v_p[_-]", l)
        
            if m:
                ms = m.group(1).split('_')
                # print "%s\t%s" % (ms, m)
                mwe = " ".join(ms)
                #if len(ms) > 2:
                #   print(mwe)
            else:
                mwe = None
        if mwe: 
            mm = re.search(r"KEYREL.PRED \"([-a-z_]+)\"", l)
            
            if mm:
                # print("%s\t%s" % (mwe, mm.group(1)))
                mwe_list.add((mwe, mm.group(1)))
                mwe_lemma_map[mm.group(1)] = mwe
    with open('data/mwe.txt', 'w') as outfile:
        for mwe in mwe_list:
            outfile.write('\t'.join(mwe))
            outfile.write('\n')
            
    # Searching for lexicon
    print("Mapping to WordNet ...")
    c = Counter()
    mwe_found = []
    mwe_notfound = []
    for mwe in mwe_list:
        print("Looking for [%s]" % (mwe[0],))
        if mwe[0] in all_senses:
            candidates = all_senses[mwe[0]]
            mwe_found.append(',"%s"' % (mwe[1],) + ': [' + ', '.join(('"%s-%s"' % (str(x.sid)[1:], x.pos) for x in candidates)) + "] # " + mwe[0])
            c.count("Found")
        else:
            c.count("Not found")
            mwe_notfound.append('\t'.join(mwe))
        c.count("Total")
    c.summarise()
    mwe_found = [ '# This file contains predicates in ERG which have been mapped to concept in WordNet', '# ' ] + mwe_notfound
    writelines(mwe_found, MWE_FOUND)
    mwe_notfound = [ '# This file contains predicates in ERG which cannot be found in WordNet', '# ' ] + mwe_notfound
    writelines(mwe_notfound, MWE_NOTFOUND)
    pred_lemma =  [ '# This file contains all VV preds in ERG and their lemmas', "# " ]
    pred_lemma += [ ",'%s' : '%s'" % (x[1], x[0]) for x in mwe_list ] 
    writelines(pred_lemma, MWE_PRED_LEMMA)
    print("All done")
    pass

def main():
    dev()
    extract_all_rel()
    # extract_mwe()
    
if __name__ == "__main__":
    main()
