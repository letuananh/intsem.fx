#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script for analysing ERG

Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2018, Le Tuan Anh <tuananh.ke@gmail.com>
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
import logging

from chirptext import TextReport, Counter
from chirptext.cli import CLIApp, setup_logging

from coolisf.mappings import PredSense
from coolisf.ergex import read_erg_lex
from coolisf.model import Predicate

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

setup_logging('logging.json', 'logs')
TRIVIAL_POS = 'navj'


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def list_preds(cli, args):
    rp = TextReport(args.output)
    lexdb = read_erg_lex()
    keyrels = set(l.keyrel for l in lexdb if l.keyrel)
    preds = [Predicate.from_string(p) for p in keyrels]
    sorted_preds = sorted(preds, key=lambda x: x.pos or '')
    # All preds
    with open('data/erg_preds_sorted.txt', 'w') as outfile:
        for pred in sorted_preds:
            outfile.write('{}\n'.format(pred))
    poses = set(p.pos for p in preds)
    trivial_preds = [p for p in preds if p.pos and p.pos in TRIVIAL_POS]
    if not args.trivial:
        preds = [p for p in preds if not p.pos or p.pos not in TRIVIAL_POS]
    interesting_poses = set(p.pos for p in preds)
    # write interesting preds to file
    c = Counter()
    with open('data/erg_preds_interesting.txt', 'w') as outfile:
        for pred in sorted(preds, key=lambda x: "cqpx".index(x.pos) if x.pos else 0):
            c.count(pred.pos if pred.pos else 'NONE')
            outfile.write('{}\n'.format(pred))
    # report
    rp.print("Interesting preds: {}".format(len(preds)))
    rp.print("Trivial preds: {}".format(len(trivial_preds)))
    rp.print("POS: {}".format(poses))
    rp.print("Interesting POS: {}".format(interesting_poses))
    c.summarise(rp)


def list_gpreds(cli, args):
    rp = TextReport(args.output)
    with open('data/erg_preds_sorted.txt', 'r') as infile:
        sorted_preds = (Predicate.from_string(l) for l in infile)
        for pred in sorted_preds:
            if pred.ptype == Predicate.GRAMMARPRED:
                rp.print(pred)
    pass


def map_preds(cli, args):
    rp = TextReport(args.output)
    ctx = PredSense.wn.ctx()
    not_found = []
    pred_file = 'data/erg_preds_interesting.txt'
    if args.all:
        pred_file = 'data/erg_preds_sorted.txt'
    name, ext = os.path.splitext(pred_file)
    not_found_file = name + "_notfound" + ext
    with open(pred_file, 'r') as infile:
        for p_str in infile.read().splitlines():
            p = Predicate.from_string(p_str)
            candidates = None
            if p.pos == 'x' and p.sense == 'subord':
                continue  # ignore these for now
            # if (p.pos == 'x' and p.sense == 'deg') or p.pos == 'p':
            if args.all or (p.pos and p.pos in 'xpq'):
                rp.header(p, p.lemma, p.pos, p.sense)
                candidates = PredSense.search_pred_string(p, ctx=ctx)
                for c in candidates:
                    rp.print(c.ID, c.lemmas, c.definition)
            if not candidates:
                not_found.append(p_str)
    with TextReport(not_found_file, 'w') as outfile:
        for p in not_found:
            outfile.print(p)

    if args.output:
        print("Written to: {}".format(args.output))
    print("Done")


def pred_info(cli, args):
    p = Predicate.from_string(args.pred)
    print("{}: lemma={} | pos={} | sense={}".format(args.pred, p.lemma, p.pos, p.sense))
    candidates = PredSense.search_pred_string(p)
    if candidates:
        for c in candidates:
            print(c.ID, c.lemmas, c.definition)
    else:
        print("No candidate could be found")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ISF ERG Analyser  '''
    app = CLIApp(desc='ISF ERG Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('preds', func=list_preds)
    task.add_argument('-o', '--output', help="Output")
    task.add_argument('-t', '--trivial', help="Don't remove trivial preds", action="store_true")
    # list gpreds
    task = app.add_task('gpreds', func=list_gpreds)
    task.add_argument('-o', '--output', help="Output")
    # map preds
    task = app.add_task('map', func=map_preds)
    task.add_argument('-o', '--output', help="Output")
    task.add_argument('--all', help="Map all preds", action="store_true")
    # show predicate info
    task = app.add_task('info', func=pred_info)
    task.add_argument('pred')
    # run app
    app.run()


if __name__ == "__main__":
    main()
