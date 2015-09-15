#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Integrated Semantic Framework (coolisf) interactive shell

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
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os

from delphin.interfaces import ace
from delphin.mrs.components import Pred
from chirptext.leutile import StringTool

from .model import Sentence
from .util import PredSense

##########################################
# CONFIGURATION
##########################################
GRAM_FILE = './data/erg.dat'
ACE_BIN = os.path.expanduser('~/bin/ace')
SEMCOR_TXT = 'data/semcor.txt'
TOP_K = 10


def read_data():
    return [StringTool.strip(x) for x in open(SEMCOR_TXT).readlines()]


def get_preds(dmrs):
    if dmrs:
        return [Pred.normalize_pred_string(x.pred.string) for x in dmrs.nodes]


def txt2preds(text):
    dmrses = txt2dmrs(text)
    if dmrses:
        return [get_preds(x) for x in dmrses]
    else:
        print("Can't parse the sentence [%s]" % (text,))


def txt2dmrs(text):
    s = Sentence(text)

    res = ace.parse(GRAM_FILE, text, executable=ACE_BIN)
    if res and res['RESULTS']:
        top_res = res['RESULTS']
        for mrs in top_res:
            s.add(mrs['MRS'])
    return s


def enter_sentence():
    return input("Enter a sentence (empty to exit): ")


def main():
    print("Integrated Semantic Framework has been loaded.")
    process_sentence("Hello! I am an integrated semantic framework.", verbose=False, top_k=1)
    interactive_shell()


def interactive_shell():
    while True:
        sent = enter_sentence()
        if not sent:
            break
        else:
            process_sentence(sent)
        # done


def process_sentence(sent, verbose=True, top_k=10):
    if verbose:
        print("You have entered: %s" % sent)
    tagged = txt2dmrs(sent)
    mrs_id = 1
    if tagged and tagged.mrs:
        for mrs in tagged.mrs:
            print('-' * 80)
            print("MRS #%s\n" % mrs_id)
            print(PredSense.tag_sentence(mrs))
            print('\n\n')
            mrs_id += 1
            if top_k < mrs_id:
                break
            # endif


if __name__ == "__main__":
    main()
