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

from .gold_extract import generate_gold_profile
from .gold_extract import read_ace_output
from .gold_extract import export_to_visko
from .gold_extract import read_gold_sents


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


def main():
    parser = argparse.ArgumentParser(description="CoolISF Main Application")

    tasks = parser.add_subparsers(help='Task to be done')

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
