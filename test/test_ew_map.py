#!/Usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test ERG-Wordnet mapping
Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2015, coolisf"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import unittest
import logging

from coolisf.ergex import read_erg_lex, extract_all_rel, extract_mwe, find_mwe
from coolisf.model import PredSense
from coolisf.util import Grammar

########################################################################


logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Change this to DEBUG for more information

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')
TEST_SENTENCES = 'data/bib.txt'
ACE_OUTPUT_FILE = 'data/bib.mrs.txt'


class TestMain(unittest.TestCase):

    lexdb = read_erg_lex()
    ERG = Grammar()

    def test_find_mwe(self):
        mwe_list = find_mwe()
        print(list(mwe_list)[:5])

    def test_read_erg(self):
        # get non empty rels
        nonempty = [x for x in self.lexdb if x.keyrel != '\\N']
        print(nonempty[50:100])

    def test_erg2wn(self):
        d = PredSense.search_pred_string('_test_v_1')
        self.assertEqual([str(x.synsetid) for x in d], ['02531625-v', '02533109-v', '00786458-v', '02745713-v', '01112584-v', '00920778-v', '00669970-v'])
        pass

    def test_extract_mwe(self):
        # extract_mwe()
        pass

    def test_extract_rel(self):
        # extract_all_rel()
        pass

########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
