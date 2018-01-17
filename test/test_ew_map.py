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

from chirptext.cli import setup_logging
from coolisf.ergex import read_erg_lex, find_mwe
from coolisf.mappings import PredSense
from coolisf import GrammarHub

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')
TEST_SENTENCES = 'data/bib.txt'
ACE_OUTPUT_FILE = 'data/bib.mrs.txt'


def getLogger():
    return logging.getLogger(__name__)


setup_logging(os.path.join(TEST_DIR, 'logging.json'), os.path.join(TEST_DIR, 'logs'))


# ------------------------------------------------------------------------------
# TEST SCRIPTS
# ------------------------------------------------------------------------------

class TestMain(unittest.TestCase):

    lexdb = read_erg_lex()
    ERG = GrammarHub().ERG

    def test_find_mwe(self):
        mwe_list = list(find_mwe())[:5]
        self.assertEqual(len(mwe_list), 5)

    def test_read_erg_lexdb(self):
        # get non empty rels
        nonempty = [x for x in self.lexdb if x.keyrel != '\\N']
        self.assertGreater(len(nonempty), 30000)
        for l in self.lexdb:
            self.assertTrue(l.lextype)

    def test_erg2wn(self):
        d = PredSense.search_pred_string('_test_v_1')
        self.assertEqual({str(x.synsetid) for x in d}, {'02531625-v', '02533109-v', '00786458-v', '02745713-v', '01112584-v', '00920778-v', '00669970-v'})
        pass

    def test_extend_lemma(self):
        self.assertEqual(PredSense.extend_lemma('night bird'), {'night-bird', 'night bird', 'nightbird'})
        self.assertEqual(PredSense.extend_lemma('above+all'), {'above-all', 'above+all', 'aboveall', 'above all'})

    def test_lemma_searching(self):
        ss = PredSense.search_sense({'above all'}, 'r')
        self.assertEqual({'00150671-r', '00158190-r'}, {s.ID for s in ss})

    def test_known_concepts(self):
        # test verb
        synsets = PredSense.search_pred_string('_bark_v_1')
        self.assertTrue(synsets)
        for synset in synsets:
            self.assertEqual(synset.ID.pos, 'v')
            self.assertIn('bark', synset.lemmas)
        # test noun
        synsets = PredSense.search_pred_string('_bark_n_1')
        self.assertTrue(synsets)
        for synset in synsets:
            self.assertEqual(synset.ID.pos, 'n')
            self.assertIn('bark', synset.lemmas)
        # test adj
        synsets = PredSense.search_pred_string('_quick_a_1')
        self.assertTrue(synsets)
        for synset in synsets:
            self.assertEqual(synset.ID.pos, 'a')
            self.assertIn('quick', synset.lemmas)
        # MWE
        synsets = PredSense.search_pred_string('_look_v_up')
        for synset in synsets:
            self.assertIn("look up", synset.lemmas)
        synsets = PredSense.search_pred_string('_above+all_a_1_rel')
        getLogger().debug("above+all", synsets)
        for synset in synsets:
            self.assertIn('above all', synset.lemmas)
        synsets = PredSense.search_pred_string('_above-mentioned_a_1_rel')
        getLogger().debug("above-mentioned", synsets)
        self.assertTrue(synsets)
        getLogger().debug(PredSense.search_pred_string("_allright_a_for_rel"))
        getLogger().debug(PredSense.search_pred_string("_abrasive_a_1_rel"))

    def test_known_mwe(self):
        d = PredSense.search_pred_string('_green+tea_n_1')
        self.assertEqual(d[0].synsetid, '07935152-n')


########################################################################

if __name__ == "__main__":
    unittest.main()
