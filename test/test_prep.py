#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for dynamically loading preprocessors
Latest version can be found at https://github.com/letuananh/intsem.fx

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

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, intsem.fx"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import unittest
import coolisf
from chirptext.texttaglib import TaggedSentence
from coolisf.util import PrepManager, GrammarHub

#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')


#-------------------------------------------------------------------------------
# DATA STRUCTURES
#-------------------------------------------------------------------------------

class TestMainApp(unittest.TestCase):

    def test_preps(self):
        man = PrepManager()
        man.register("mecab", "coolisf.util", "PrepMeCab")
        prep = man["mecab"]
        self.assertIsInstance(prep, coolisf.util.PrepMeCab)
        self.assertEqual(prep.name, "mecab")
        actual = prep.process("猫が好きです。")
        expected = "猫 が 好き です 。 \n"
        self.assertEqual(actual, expected)

    def test_dekoprep(self):
        man = PrepManager()
        man.register("deko", "coolisf.util", "PrepDeko")
        prep = man["deko"]
        sent = prep.process("猫が好きです。")
        self.assertIsInstance(sent, coolisf.model.Sentence)
        self.assertIsInstance(sent.shallow, TaggedSentence)
        self.assertEqual(sent.shallow[0].label, "猫")
        self.assertEqual(sent.shallow[0].pos, "名詞-一般")

    def test_auto_reg(self):
        # config.json should auto-register all of these preps
        ghub = GrammarHub()
        sent = ghub.JACYDK.parse("猫が好きです。")
        self.assertIsInstance(sent, coolisf.model.Sentence)
        # verify shallow
        self.assertIsInstance(sent.shallow, TaggedSentence)
        self.assertEqual(sent.shallow[0].label, "猫")
        self.assertEqual(sent.shallow[0].pos, "名詞-一般")
        # verify deep
        self.assertIsNotNone(sent[0].dmrs())
        expected = ['udef_q_rel', '_neko_n_rel', '_suki_a_1_rel']
        actual = sent[0].dmrs().preds()
        self.assertEqual(expected, actual)

    def test_erg_nltk(self):
        ghub = GrammarHub()
        sent = ghub.ERG_NLTK.parse("It rains.")
        self.assertIsNotNone(sent.shallow)
        print(sent.shallow.tokens)


#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
