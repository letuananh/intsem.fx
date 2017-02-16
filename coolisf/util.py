#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Utility functions

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
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import logging
from delphin.interfaces import ace
from delphin.mrs.components import Pred

from chirptext.leutile import Counter
from chirptext.texttaglib import writelines

from .model import Sentence

##########################################
# CONFIGURATION
##########################################

ERG_GRAM_FILE = './data/erg.dat'
ACE_BIN = os.path.expanduser('~/bin/ace')
ACE_ARGS = ['-n', '5']
SEMCOR_TXT = 'data/semcor.txt'
TOP_K = 10

logger = logging.getLogger(__name__)


########################################################################

def read_ace_output(ace_output_file):
    logger.info("Reading parsed MRS from %s..." % (ace_output_file,))
    c = Counter()
    items = []
    sentences = []
    skipped = []
    with open(ace_output_file, 'r') as input_mrs:
        current_sid = 0
        while True:
            current_sid += 1
            line = input_mrs.readline()
            if line.startswith('SENT'):
                mrs_line = input_mrs.readline()
                # item = [line, mrs_line]
                s = Sentence(line[5:], sid=current_sid)
                sentences.append(s)
                while mrs_line.strip():
                    s.add(mrs_line)
                    mrs_line = input_mrs.readline()
                input_mrs.readline()
                c.count('sent')
                c.count('total')
            elif line.startswith('SKIP'):
                skipped.append(line[5:].strip())
                items.append([line])
                input_mrs.readline()
                input_mrs.readline()
                c.count('skip')
                c.count('total')
            else:
                break
    c.summarise()
    writelines(skipped, ace_output_file + '.skipped.txt')
    return sentences


def get_preds(dmrs):
    if dmrs:
        return [Pred.normalize_pred_string(x.pred.string) for x in dmrs.nodes]


class Grammar:
    def __init__(self, gram_file=ERG_GRAM_FILE, cmdargs=ACE_ARGS, ace_bin=ACE_BIN):
        self.gram_file = gram_file
        self.cmdargs = cmdargs
        self.ace_bin = ace_bin

    def txt2preds(self, text):
        dmrses = self.parse(text)
        if dmrses:
            return [get_preds(x) for x in dmrses]
        else:
            logging.warning("Can't parse the sentence {}".format(text))

    def parse(self, text, parse_count=None):
        s = Sentence(text)
        args = self.cmdargs
        if parse_count:
            args += ['-n', str(parse_count)]
        with ace.AceParser(self.gram_file, executable=self.ace_bin, cmdargs=args) as parser:
            result = parser.interact(text)
            if result and result['RESULTS']:
                top_res = result['RESULTS']
                for mrs in top_res:
                    s.add(mrs['MRS'])
        return s


def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
