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

from coolisf.ergex import read_erg_lex, find_mwe
from coolisf.model import PredSense
from coolisf import GrammarHub

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Change this to DEBUG for more information

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')
TEST_SENTENCES = 'data/bib.txt'
ACE_OUTPUT_FILE = 'data/bib.mrs.txt'


# ------------------------------------------------------------------------------
# TEST SCRIPTS
# ------------------------------------------------------------------------------

class TestMain(unittest.TestCase):

    lexdb = read_erg_lex()
    ERG = GrammarHub().ERG

    def test_find_mwe(self):
        mwe_list = list(find_mwe())[:5]
        self.assertEqual(len(mwe_list), 5)

    def test_read_erg(self):
        # get non empty rels
        nonempty = [x for x in self.lexdb if x.keyrel != '\\N']
        self.assertGreater(len(nonempty), 30000)

    def test_erg2wn(self):
        d = PredSense.search_pred_string('_test_v_1')
        self.assertEqual([str(x.synsetid) for x in d], ['02531625-v', '02533109-v', '00786458-v', '02745713-v', '01112584-v', '00920778-v', '00669970-v'])
        pass

    def test_known_concepts(self):
        preds = PredSense.search_pred_string('_bark_v_1')
        for p in preds:
            self.assertEqual((p.synsetid.pos, p.lemma), ('v', 'bark'))
        preds = PredSense.search_pred_string('_bark_n_1')
        for p in preds:
            self.assertEqual((p.synsetid.pos, p.lemma), ('n', 'bark'))
        d = PredSense.search_pred_string('_dog_v_1')
        self.assertTrue(d)
        d = PredSense.search_pred_string('_look_v_up')
        self.assertTrue(d)

    def test_known_mwe(self):
        d = PredSense.search_pred_string('_green+tea_n_1')
        self.assertEqual(d[0].synsetid, '07935152-n')


########################################################################

if __name__ == "__main__":
    unittest.main()
