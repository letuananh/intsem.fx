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
__credits__ = []
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
    r.print(len(sentences))

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


def validate_goldtags(args):
    r = TextReport('data/valgold.txt')
    from coolisf.gold_extract import read_gold_sentences
    sents = read_gold_sentences()
    for sent in sents:
        if len(sent) == 0:
            print("WARNING: {} is not parsed".format(sent.sid))
        for d in sent:
            extract_tags(r, d.dmrs(), sent.sid)


def extract_tags(report, d, sentid=None):
    d.json()  # call this to extract tags and sort them too
    for nodeid, tags in d.tags.items():
        ep = d.obj().ep(int(nodeid))
        tag_str = []
        for tag in tags:
            tag_str.append('\t'.join((str(tag[0].synsetid), tag[0].lemma, tag[1].upper())))
        cfrom, cto, surface = d.fix_tokenization(ep, d.parse.sent.text)
        report.print('\t'.join((str(sentid), str(cfrom), str(cto), '\t'.join(tag_str))))


def mine_stuff():
    print("Yay")


########################################################################

def main():
    ''' ISF Miner
    '''
    parser = argparse.ArgumentParser(description="ISF Miner")

    # Positional argument(s)
    task_parsers = parser.add_subparsers(help='Task to be done')

    mine_preds_task = task_parsers.add_parser('mine')
    mine_preds_task.set_defaults(func=mine_preds)

    find_compound_task = task_parsers.add_parser('fcomp')
    find_compound_task.add_argument('filepath')
    find_compound_task.set_defaults(func=find_compound)

    # validate gold tags
    valgold_task = task_parsers.add_parser('vgold')
    valgold_task.set_defaults(func=validate_goldtags)

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
