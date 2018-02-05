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

import logging

from chirptext import TextReport, Counter
from chirptext.cli import CLIApp, setup_logging

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
    # run app
    app.run()


if __name__ == "__main__":
    main()
