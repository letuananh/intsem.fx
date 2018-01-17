#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Integrated Semantic Framework (coolisf) main application

`coolisf` is read `kul-eye-es-ef` officially (sometimes kul-is-f)

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
__version__ = "0.2"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import sys
import gzip
import argparse
import logging

from chirptext.cli import CLIApp, setup_logging
from chirptext import header, confirm, TextReport, FileHelper, Counter
from chirptext.texttaglib import TagInfo

from .dao import read_tsdb
from .ghub import GrammarHub
from .gold_extract import generate_gold_profile
from .util import read_ace_output
from .gold_extract import export_to_visko
from .gold_extract import read_gold_sents
from .model import Document
from .dao.textcorpus import RawCollection

########################################################################

OUTPUT_DMRS = 'dmrs'
OUTPUT_MRS = 'mrs'
OUTPUT_XML = 'xml'
OUTPUT_FORMATS = [OUTPUT_DMRS, OUTPUT_MRS, OUTPUT_XML]

setup_logging('logging.json', 'logs')


########################################################################

def to_visko(cli, args):
    ''' Export MRS to VISKO '''
    # determine docpath
    if args.bibloc:
        visko_data_dir = os.path.abspath(args.bibloc)
    else:
        # default bibloc
        visko_data_dir = os.path.expanduser('~/workspace/visualkopasu/data/biblioteche')
    export_path = os.path.join(visko_data_dir, args.biblioteca, args.corpus, args.doc)
    print("Biblioteche location: {}".format(visko_data_dir))
    print("Document location   : {}".format(export_path))
    # which file to export
    if args.file is not None:
        # export MRS file
        sents = read_ace_output(args.file)  # e.g. data/wndefs.nokey.mrs.txt
        if args.topk:
            sents = sents[:int(args.topk)]
    else:
        if input("No MRS file provided. Proceed to export gold profile to Visko (yes/no)? ").lower() in ['y', 'yes']:
            print("Exporting gold profile to Visko")
            sents = read_gold_sents()
        else:
            print("Aborted")
            return
    export_to_visko(sents, export_path)


def parse_isf(cli, args):
    ''' Process raw text file '''
    # verification
    if not os.path.isfile(args.infile):
        print("Error. File does not exist. (provided: {})".format(args.infile))
    if args.outfile and os.path.exists(args.outfile):
        if not confirm("Output file exists. Do you want to continue (Y/N)? "):
            print("Program aborted.")
            return
    # process
    header("Processing file: {}".format(args.infile))
    report = TextReport(args.outfile)
    ghub = GrammarHub()
    lines = FileHelper.read(args.infile).splitlines()
    for sent in ghub.ERG_ISF.parse_many_iterative(lines, parse_count=args.n, ignore_cache=args.nocache):
        sent.tag_xml(method=args.wsd)
        report.writeline(sent.to_xml_str(pretty_print=not args.compact))
        report.writeline("\n\n")


def extract_tsdb(cli, args):
    ''' Read parsed sentences from a TSDB profile '''
    if not os.path.isdir(args.path):
        print("TSDB profile does not exist (path: {})".format(args.path))
    else:
        doc = read_tsdb(args.path)
        print("Found sentences: {}".format(len(doc)))
        doc_xml_str = doc.to_xml_str(pretty_print=not args.compact, with_dmrs=not args.nodmrs)
        if args.output:
            if args.output.endswith('.gz'):
                with gzip.open(args.output, 'wt') as outfile:
                    outfile.write(doc_xml_str)
            else:
                with open(args.output, 'wt') as outfile:
                    outfile.write(doc_xml_str)
        else:
            print(doc_xml_str)


def parse_text(cli, args):
    ''' Analyse a text '''
    ghub = GrammarHub()
    text = args.input
    result = ghub.parse(text, args.grammar, args.n, args.wsd, args.nocache)
    if result is not None and len(result) > 0:
        report = TextReport(args.output)
        if args.format == OUTPUT_DMRS:
            report.header(result)
            for reading in result:
                report.writeline(reading.dmrs().tostring(pretty_print=not args.compact))
                report.writeline()
        elif args.format == OUTPUT_XML:
            result.tag_xml()
            report.writeline(result.to_xml_str(pretty_print=not args.compact))
        elif args.format == OUTPUT_MRS:
            report.header(result)
            for reading in result:
                report.writeline(reading.mrs().tostring(pretty_print=not args.compact))
                report.writeline()


def parse_bib(cli, args):
    c = Counter()
    ghub = GrammarHub()
    bib_path = FileHelper.abspath(args.input)
    if not os.path.isdir(bib_path):
        cli.logger.warning("Raw biblioteca could not be found at {}".format(bib_path))
        exit()
    cli.logger.info("Analysing biblioteca {}".format(bib_path))
    # validate output
    if not args.output or not os.path.isdir(args.output):
        cli.logger.warning("Output directory does not exist")
        exit()
    bib = RawCollection(bib_path)
    corpuses = bib.get_corpuses()
    print("Available corpuses: {}".format(len(corpuses)))
    c.update({"Corpuses": len(corpuses)})
    for corpus in corpuses:
        print("Processing corpus: {} ({})".format(corpus.name, corpus.title))
        # create dir for corpus
        corpus_path = os.path.join(args.output, corpus.name)
        if not os.path.exists(corpus_path):
            os.makedirs(corpus_path)
        for doc in corpus.get_documents():
            c.count("Documents")
            sents = list(doc.read_sentences())
            c.update({'Sentences': len(sents)})
            print("Processing document: {} {} | Size: {}".format(doc.name, doc.title, len(sents)))
            doc_path = os.path.join(corpus_path, doc.name + '.xml')
            doc_isf = Document(name=doc.name, title=doc.title)
            sent_texts = [s.text for s in sents]
            # parse document
            report = TextReport(doc_path)
            for sent in ghub.ERG_ISF.parse_many_iterative(sent_texts, parse_count=args.n, ignore_cache=args.nocache):
                sent.tag_xml(method=args.wsd)
                print("Processed: {}".format(sent.text))
                doc_isf.add(sent)
            report.writeline(doc_isf.to_xml_str(pretty_print=not args.compact))
    c.summarise()


def isf_config_logging(args):
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('coolisf.ghub').setLevel(logging.DEBUG)
        logging.getLogger('coolisf.morph').setLevel(logging.DEBUG)
        logging.getLogger('coolisf.processors').setLevel(logging.DEBUG)


def main():
    app = CLIApp("CoolISF Main Application", logger=__name__, config_logging=isf_config_logging)

    task = app.add_task('parse', func=parse_isf)
    task.add_argument('infile', help='Path to input text file')
    task.add_argument('outfile', help='Path to store results', nargs="?", default=None)
    task.add_argument('-n', help='Maximum parse count', default=None)
    task.add_argument('--nocache', help='Do not cache parse result', action='store_true', default=None)
    task.add_argument('--wsd', help='Word Sense Disambiguator', default=TagInfo.LELESK)
    task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")

    task = app.add_task('text', func=parse_text)
    task.add_argument('input', help='Any text')
    task.add_argument('-g', '--grammar', help="Grammar name", default="ERG_ISF")
    task.add_argument('-n', help="Only show top n parses", default=None)
    task.add_argument('--wsd', help="Word-Sense Disambiguator", default=TagInfo.LELESK)
    task.add_argument('--nocache', help='Do not cache parse result', action='store_true', default=None)
    task.add_argument('-f', '--format', help='Output format', choices=OUTPUT_FORMATS, default=OUTPUT_DMRS)
    task.add_argument('-o', '--output', help="Write output to path")
    task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")

    # batch processing a raw text corpus
    task = app.add_task('bib', func=parse_bib)
    task.add_argument('input', help='Path to raw biblioteca')
    task.add_argument('-g', '--grammar', help="Grammar name", default="ERG_ISF")
    task.add_argument('-n', help="Only show top n parses", default=None)
    task.add_argument('--wsd', help="Word-Sense Disambiguator", default=TagInfo.LELESK)
    task.add_argument('--nocache', help='Do not cache parse result', action='store_true', default=None)
    task.add_argument('-f', '--format', help='Output format', choices=OUTPUT_FORMATS, default=OUTPUT_DMRS)
    task.add_argument('-o', '--output', help="Write output to path")
    task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")
    # Create ISF gold profile
    task = app.add_task('gold', lambda cli, args: generate_gold_profile(), help='Extract gold profile')

    # Extract sentences from TSDB profile
    tsdb_task = app.add_task('tsdb', func=extract_tsdb)
    tsdb_task.add_argument('path', help='Path to TSDB profile folder')
    tsdb_task.add_argument('output', help='Save extracted sentences to a file', nargs="?", default=None)
    tsdb_task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")
    tsdb_task.add_argument('--nodmrs', help="Do not generate DMRS XML", action="store_true")

    task = app.add_task('export', func=to_visko)
    task.add_argument('-f', '--file', help='MRS file')
    task.add_argument('biblioteca')
    task.add_argument('corpus')
    task.add_argument('doc')
    task.add_argument('-k', '--topk', help='Only extract top K sentences')
    task.add_argument('-b', '--bibloc', help='Path to Biblioteche folder (corpus collection root)')

    app.run()


if __name__ == "__main__":
    main()
