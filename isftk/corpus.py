#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script for processing corpuses

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
from collections import defaultdict as dd

from chirptext import TextReport
from chirptext.cli import CLIApp, setup_logging

from coolisf.common import write_file
from coolisf.model import Document, Sentence
from .gold import patch_gold_sid

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def extract_mrs(cli, args):
    ''' Remove everything except MRS raw string '''
    doc = Document.from_file(args.path)
    if args.patchsid:
        patch_gold_sid(doc, seed=args.seed)
    doc_str = doc.to_xml_str(with_shallow=args.shallow, with_dmrs=args.dmrs)
    write_file(doc_str, args.output)
    print("Done!")


def remove_tags(cli, args):
    ''' Remove tags from ISF doc '''
    doc = Document.from_file(args.path)
    new_doc = Document(name=doc.name, corpusID=doc.corpusID, title=doc.title, grammar=doc.grammar, tagger=doc.tagger, parse_count=doc.parse_count, lang=doc.lang)
    if args.nogold:
        print("Only gold tags will be removed")
    for sent in doc:
        new_sent = Sentence.from_xml_node(sent.to_xml_node())
        new_doc.add(new_sent)
        for reading in new_sent:
            if not args.nogold:
                reading.dmrs().tags = dd(list)
            else:
                # only remove gold
                # if len(reading.dmrs().tags.items()) == 0:
                #     getLogger().warning("No tag for {}".format(sent.ident))
                reading.dmrs().find_tags()
                for nodeid, tags in reading.dmrs().tags.items():
                    remove_tags = []
                    for tag in tags:
                        if tag.method == 'gold':
                            # remove it
                            remove_tags.append(tag)
                    # remove them all
                    for tag in remove_tags:
                        getLogger().debug("removing {}".format(tag))
                        tags.remove(tag)
        new_sent.tag_xml()
    # write output to file
    if args.output:
        write_file(new_doc.to_xml_str(), args.output)
    else:
        TextReport().write(new_doc.to_xml_str())


def count_senses(cli, args):
    ''' Show stats of a document '''
    doc = Document.from_file(args.path)
    sense_count = 0
    dmrs_count = 0
    for sent in doc:
        for reading in sent:
            dmrs_count += 1
            sense_count += len(reading.dmrs().tags)
    print("Sentences: {}".format(len(doc)))
    print("DMRSes: {}".format(dmrs_count))
    print("Senses: {}".format(sense_count))
    print("Done")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' Corpus toolkit'''
    app = CLIApp(desc='Corpus processors', logger=__name__)
    # add tasks
    task = app.add_task('notag', func=remove_tags)
    task.add_argument('path', help='Path to document file (*.xml or *.xml.gz)')
    task.add_argument('-o', '--output', help='Output file')
    task.add_argument('--nogold', action="store_true")
    # compress
    task = app.add_task('mrs', func=extract_mrs)
    task.add_argument('path', help='Path to document file (*.xml or *.xml.gz)')
    task.add_argument('-o', '--output', help='Output file')
    task.add_argument('-f', '--patchsid', help='Force patching sentences Ids', action='store_true')
    task.add_argument('--seed', help='Starting number', type=int, default=10000)
    task.add_argument('--shallow', help='Keep shallow', action='store_true')
    task.add_argument('--dmrs', help='Keep DMRS', action='store_true')
    # count senses
    task = app.add_task('stats', func=count_senses)
    task.add_argument('path', help='Path to document file (*.xml or *.xml.gz)')
    task.add_argument('-o', '--output', help='Output file')

    # run app
    app.run()


if __name__ == "__main__":
    main()
