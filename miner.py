#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ISF Gold Miner
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

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2016, ISF"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
import collections
import string

from chirptext.leutile import TextReport

from coolisf.gold_extract import *
from coolisf.model import Sentence
from coolisf.util import Grammar

########################################################################


is_nounep = lambda e : e and len(e.args) == 1 and 'ARG0' in e.args and e.pred.pos == 'n'


# A sample MRS
text = 'The cat dog barks.'
mrs_str = '''[ LTOP: h0
INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
RELS: < [ _the_q_rel<0:3> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
 [ compound_rel<4:11> LBL: h7 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x9 [ x IND: + PT: notpro ] ]
 [ udef_q_rel<4:7> LBL: h10 ARG0: x9 RSTR: h11 BODY: h12 ]
 [ "_cat_n_1_rel"<4:7> LBL: h13 ARG0: x9 ]
 [ "_dog_n_1_rel"<8:11> LBL: h7 ARG0: x3 ]
 [ "_bark_v_1_rel"<12:18> LBL: h1 ARG0: e2 ARG1: x3 ] >
HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 >
ICONS: < > ]'''
mrs = simplemrs.loads_one(mrs_str)

def mine_compoundnoun(text, mrs):
    compounds = []
    if mrs:
        noun_vars = set()
        eps = mrs.eps()
        # Find all noun first
        for ep in eps:
            if is_nounep(ep):
                noun_vars.add(ep.args['ARG0'])
        # find all compounds
        for ep in eps:
            if ep.pred.string == 'compound_rel':
                surface_str = text[ep.cfrom:ep.cto].lower().strip().strip(string.punctuation)
                print(surface_str[-1], surface_str)
                compounds.append((ep, surface_str))                
    return compounds

def mine_preds(args):
    r = TextReport('data/mining.txt')
    r.header('Pred mining')
    sid_gold_map = read_gold_tags()
    sentences = read_gold_mrs()
    report.print(len(sentences))

    # find all prepositions
    prepset = set()
    sentset = set()
    nounset = set()
    prepverbs = collections.Counter()
    prepverbsofto = collections.Counter()
    compounds = collections.Counter()
    for sent in sentences[:]:
        if sent.mrs:
            compounds.update([ x[1] for x in mine_compoundnoun(sent.text, sent.mrs[0].mrs()) ])
            for ep in sent.mrs[0].mrs().eps():
                if is_nounep(ep):
                    nounset.add(ep.pred.string)
                if ep.pred.pos == 'p':
                    prepset.add(ep.pred.lemma)
            preds = sent.mrs[0].preds()
            for pred in preds:
                if 'compound' in pred.label:
                    # r.writeline(sent.mrs[0].text)
                    # r.writeline('\n\n')
                    # r.writeline(sent.mrs[0].mrs())
                    sentset.add(sent.text)
                    
    # capture verb-preps
    for sent in sentences:
        if sent.mrs:
            for ep in sent.mrs[0].mrs().eps():
                if ep.pred.sense in ('of','to'):
                    prepverbsofto.update([ep.pred.string])
                elif ep.pred.sense in prepset:
                    prepverbs.update([ep.pred.string])

    r.header('Prep verb')
    for k,v in prepverbs.most_common():
        r.writeline('{} : {}'.format(k,v))
    
    r.header('Verb_of|to')    
    for k,v in prepverbsofto.most_common():
        r.writeline('{} : {}'.format(k,v))
    
    r.header('Prepositions')
    for p in prepset:
        r.writeline(p)

    r.writeline(nounset)

    r.header('Most common compounds')
    for k,v in compounds.most_common():
        r.writeline('{} : {}'.format(k,v))
        
    r.header('By alphabet')
    kvs = [(k, compounds[k]) for k in sorted(compounds.keys())]
    for k,v in kvs:
        r.writeline('{} : {}'.format(k,v))

    # print(sentset)
    # print(len(sentset))


def dev_mode(args):
    print("Quick dev mode")
    # parse a sentence using ERG
    s = Grammar().txt2dmrs('Dogs are funnier than Asian tiger mosquitoes.')
    # print MRS in different formats
    print("var text = '%s';" % (s.text))
    print("// RAW MRS: %s" % (s.mrs[0].text))
    print("var mrs_json = '%s';" % s.mrs[0].mrs_json())
    print("var dmrs_json = '%s';" % s.mrs[0].dmrs_json())
    print(s.mrs[0].dmrs_str())
    print("Done")


def find_compound(args):
    raw_file = args.filepath + '.txt'
    mrs_file = args.filepath + '.mrs.txt'
    print("Looking for compounds from %s" % raw_file)
    from coolisf.gold_extract import read_ace_output
    sentences = read_ace_output(mrs_file)
    # look for compounds
    with open(args.filepath + '.mrs.compound_only.txt', 'w') as cpfile:
        for s in sentences:
            for mrs in s.mrs:
                if('compound' in mrs):
                    print("{}\t{}\t{}".format(s.sid, s.text, mrs))
                    cpfile.write('SENT: {}\n{}\n\n\n'.format(s.text, mrs))
    print("Done")

########################################################################

def main():
    ''' ISF Miner
    '''

    parser = argparse.ArgumentParser(description="ISF Miner")

    # Positional argument(s)
    task_parsers = parser.add_subparsers(help='Task to be done')

    mine_preds_task = task_parsers.add_parser('mine')
    mine_preds_task.set_defaults(func=mine_preds)

    dev_task = task_parsers.add_parser('dev')
    dev_task.set_defaults(func=dev_mode)

    find_compound_task = task_parsers.add_parser('fcomp')
    find_compound_task.add_argument('filepath')
    find_compound_task.set_defaults(func=find_compound)

    # Optional argument(s)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    # Main script
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        # mine_preds()
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        args.func(args)

if __name__ == "__main__":
    main()
