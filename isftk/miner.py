#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script for mining gold

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
from chirptext import texttaglib as ttl
from coolisf.model import Document

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def list_preds(cli, args):
    ''' List used predicates '''
    output = TextReport(args.output)
    doc = Document.from_file(args.path)
    c = Counter()
    print("Found sentences: {}".format(len(doc)))
    for sent in doc:
        for reading in sent:
            c.update(n.predstr for n in reading.dmrs().layout.nodes)
    c.summarise(output)


def doc_stats(cli, args):
    ''' Show document statistics '''
    doc = Document.from_file(args.path)  # input
    output = TextReport(args.output)  # output
    stats = Counter()
    pred_counter = Counter()
    empty_sentences = []
    unknown_preds = Counter()
    all_pos = Counter()
    not_found = None
    if args.ttl:
        ttl_doc = ttl.Document.read_ttl(args.ttl)
        not_found = set(s.ID for s in ttl_doc).difference(s.ident for s in doc)
    for sent in doc:
        stats.count("Sentences")
        if not len(sent):
            stats.count("Sentences-empty")
            empty_sentences.append(sent.ident)
        for reading in sent:
            stats.count("Readings")
            stats['Predicates'] += len(reading.dmrs().layout.nodes)
            # pred_counter.update(n.predstr for n in reading.dmrs().layout.nodes)
            for n in reading.dmrs().layout.nodes:
                if n.pred.pos == 'u' and n.pred.sense == 'unknown':
                    stats.count("Unnown predicates")
                    if '/' in n.pred.lemma:
                        try:
                            lemma, pos = n.pred.lemma.rsplit('/', 1)
                        except:
                            getLogger().warning("Invalid unknown pred: {}".format(n.pred))
                            raise
                        all_pos.count(pos)
                        unknown_preds.count((str(n.pred), lemma, pos))
                    else:
                        stats.count("UFO")
                else:
                    stats.count("Known predicates")
                    pred_counter.count(n.predstr)
    output.header("Summary", level="h0")
    stats.summarise(output)
    output.header("Empty sentences")
    output.print("\n".join(empty_sentences))
    if not_found is not None:
        output.header("Missing from TTL")
        for sid in not_found:
            output.print(sid)
    output.header("Unknown preds POS")
    for pos, count in all_pos.most_common():
        output.print(pos, count, separator='\t')
    output.header("Unknown preds")
    for (pred, lemma, pos), count in unknown_preds.most_common():
        output.print(pred, lemma, pos, count, separator='\t')
    output.header("Known preds", level="h1")
    pred_counter.summarise(output)


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ISF Gold miner '''
    app = CLIApp(desc='ISF Gold mining Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('preds', func=list_preds)
    task.add_argument('path', help="Path to document file")
    task.add_argument('-o', '--output', help='Output file', default=None)
    # stats
    task = app.add_task('stats', func=doc_stats)
    task.add_argument('path', help="Path to document file")
    task.add_argument('-o', '--output', help='Output file', default=None)
    task.add_argument('--ttl', help='Path to TTL doc')
    # run app
    app.run()


if __name__ == "__main__":
    main()
