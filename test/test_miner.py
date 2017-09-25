#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for mining script
Latest version can be found at https://github.com/letuananh/coolisf

References:
    Python unittest documentation:
        https://docs.python.org/3/library/unittest.html
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 0257 - Python Docstring Conventions:
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

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, coolisf"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import unittest

from chirptext import FileHelper, header

from miner import analyse_compound
from coolisf import GrammarHub
from coolisf.dao.ruledb import ChunkDB

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
CHUNKDB = FileHelper.abspath("data/chunks.db")
TEST_GOLD_DIR = 'data'
ghub = GrammarHub()
ERG = ghub.ERG


# ------------------------------------------------------------------------------
# DATA STRUCTURES
# ------------------------------------------------------------------------------

class TestMiningPred(unittest.TestCase):

    db = ChunkDB(CHUNKDB)

    def test_parsing(self):
        ghub = GrammarHub()
        # noun
        sent = ghub.ERG.parse('dog', extra_args=['-r', 'root_wn'])
        self.assertGreater(len(sent), 0)
        dmrs = sent[0].dmrs().obj()
        eps = dmrs.eps()
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].pred.pos, 'n')
        # verb
        sent = ghub.ERG.parse('love', extra_args=['-r', 'root_wn_v'])
        self.assertGreater(len(sent), 0)
        dmrs = sent[0].dmrs().obj()
        eps = dmrs.eps()
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].pred.pos, 'v')
        # adjective
        sent = ghub.ERG.parse('nice', extra_args=['-r', 'root_wn'])
        self.assertGreater(len(sent), 0)
        dmrs = sent[0].dmrs().obj()
        eps = dmrs.eps()
        print(sent[0].mrs())
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].pred.pos, 'a')
        # test iterative parsing
        words = ['drink', 'eat', 'eat', 'drink']
        for parses in ghub.ERG.parse_many_iterative(words, extra_args=['-r', 'root_frag'], ignore_cache=True):
            header(parses)
            for p in parses:
                print(p.mrs())

    def test_parse_word(self):
        s = ERG.parse('burp')
        dmrs = s[0].dmrs().layout
        head = dmrs.top['ARG']
        self.assertEqual(head.pred.lemma, 'burp/NN')
        self.assertEqual(head.pred.pos, 'u')
        self.assertEqual(head.pred.sense, 'unknown')

    def test_mining(self):
        with self.db.ctx() as ctx:
            words = self.db.get_words(lemma="water ski", pos="v", limit=10, ctx=ctx)
            self.assertTrue(words)
            self.assertTrue(words[0].to_isf()[0].dmrs())

    def test_compound(self):
        with self.db.ctx() as ctx:
            result = analyse_compound(self.db, ctx, limit=2)
            self.assertTrue(result)


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
