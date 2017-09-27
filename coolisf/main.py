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
import argparse

from chirptext import header, confirm, TextReport, FileHelper
from chirptext.texttaglib import TagInfo

from .ghub import GrammarHub
from .gold_extract import generate_gold_profile
from .util import read_ace_output
from .gold_extract import export_to_visko
from .gold_extract import read_gold_sents

########################################################################

OUTPUT_DMRS = 'dmrs'
OUTPUT_MRS = 'mrs'
OUTPUT_XML = 'xml'
OUTPUT_FORMATS = [OUTPUT_DMRS, OUTPUT_MRS, OUTPUT_XML]


########################################################################

def to_visko(args):
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


def parse_isf(args):
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
        sent.tag_xml(method=args.tagger)
        report.writeline(sent.to_xml_str(pretty_print=not args.compact))
        report.writeline("\n\n")


def parse_text(args):
    ghub = GrammarHub()
    text = args.input
    result = ghub.parse(text, args.grammar, args.n, args.wsd, args.nocache)
    if result is not None and len(result) > 0:
        report = TextReport(args.output)
        if args.format == OUTPUT_DMRS:
            report.header(result)
            for reading in result:
                report.writeline(reading.dmrs().tostring(pretty_print=not args.compact))
        elif args.format == OUTPUT_XML:
            result.tag_xml()
            report.writeline(result.to_xml_str(pretty_print=not args.compact))
        elif args.format == OUTPUT_MRS:
            report.header(result)
            for reading in result:
                report.writeline(reading.mrs().tostring(pretty_print=not args.compact))


def main():
    parser = argparse.ArgumentParser(description="CoolISF Main Application")

    tasks = parser.add_subparsers(help='Task to be done')

    parse_task = tasks.add_parser('parse', help='Process raw text file')
    parse_task.add_argument('infile', help='Path to input text file')
    parse_task.add_argument('outfile', help='Path to store results', nargs="?", default=None)
    parse_task.add_argument('-n', help='Maximum parse count', default=None)
    parse_task.add_argument('--nocache', help='Do not cache parse result', action='store_true', default=None)
    parse_task.add_argument('--tagger', help='Word Sense Tagger', default=TagInfo.LELESK)
    parse_task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")
    parse_task.set_defaults(func=parse_isf)

    text_task = tasks.add_parser('text', help='Analyse a text')
    text_task.add_argument('input', help='Any text')
    text_task.add_argument('-g', '--grammar', help="Grammar name", default="ERG_ISF")
    text_task.add_argument('-n', help="Only show top n parses", default=None)
    text_task.add_argument('--wsd', help="Word-Sense Disambiguation engine", default=TagInfo.LELESK)
    text_task.add_argument('--nocache', help='Do not cache parse result', action='store_true', default=None)
    text_task.add_argument('-f', '--format', help='Output format', choices=OUTPUT_FORMATS, default=OUTPUT_DMRS)
    text_task.add_argument('-o', '--output', help="Write output to path")
    text_task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")
    text_task.set_defaults(func=parse_text)

    gold_task = tasks.add_parser('gold', help='Extract gold profile')
    gold_task.set_defaults(func=lambda arsg: generate_gold_profile())

    export_task = tasks.add_parser('export', help='Export MRS to VISKO')
    export_task.add_argument('-f', '--file', help='MRS file')
    export_task.add_argument('biblioteca')
    export_task.add_argument('corpus')
    export_task.add_argument('doc')
    export_task.add_argument('-k', '--topk', help='Only extract top K sentences')
    export_task.add_argument('-b', '--bibloc', help='Path to Biblioteche folder (corpus collection root)')
    export_task.set_defaults(func=to_visko)

    if len(sys.argv) == 1:
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        args.func(args)
    pass


if __name__ == "__main__":
    main()
