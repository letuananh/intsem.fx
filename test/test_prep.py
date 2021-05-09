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

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
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

########################################################################

import unittest
import coolisf
import logging
from texttaglib.chirptext import texttaglib as ttl
from coolisf.model import Reading
from coolisf import GrammarHub
from coolisf.processors import ProcessorManager


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestPosts(unittest.TestCase):

    def test_preps(self):
        man = ProcessorManager()
        man.register("isf", "coolisf.processors.basic", "PostISF")
        prep = man["isf"]
        self.assertIsInstance(prep, coolisf.processors.basic.PostISF)
        self.assertEqual(prep.name, "isf")
        p = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop-or-ques ]
  RELS: < [ unknown<0:12> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ udef_q<0:12> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _big_a_1<0:3> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x4 ]
          [ _bad_a_at<4:7> LBL: h8 ARG0: e10 [ e SF: prop ] ARG1: x4 ARG2: i11 ]
          [ _wolf_n_1<8:12> LBL: h8 ARG0: x4 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 > ]""")
        prep.process(p)
        self.assertEqual(p.dmrs().preds(), ['unknown_rel', 'udef_q_rel', '_big+bad+wolf_n_1_rel'])


class TestPreps(unittest.TestCase):

    def test_preps(self):
        man = ProcessorManager()
        man.register("mecab", "coolisf.processors.jp_basic", "PrepMeCab")
        prep = man["mecab"]
        self.assertIsInstance(prep, coolisf.processors.jp_basic.PrepMeCab)
        self.assertEqual(prep.name, "mecab")
        actual = prep.process("猫が好きです。")
        expected = "猫 が 好き です 。 "
        self.assertEqual(actual, expected)

    def test_dekoprep(self):
        man = ProcessorManager()
        man.register("deko", "coolisf.processors.jp_basic", "PrepDeko")
        prep = man["deko"]
        sent = prep.process("猫が好きです。")
        self.assertIsInstance(sent, coolisf.model.Sentence)
        self.assertIsInstance(sent.shallow, ttl.Sentence)
        self.assertEqual(sent.shallow[0].text, "猫")
        self.assertEqual(sent.shallow[0].pos, "名詞-一般")

    def test_auto_reg(self):
        # config.json should auto-register all of these preps
        ghub = GrammarHub()
        sent = ghub.JACYDK.parse("猫が好きです。")
        self.assertIsInstance(sent, coolisf.model.Sentence)
        # verify shallow
        self.assertIsInstance(sent.shallow, ttl.Sentence)
        self.assertEqual(sent.shallow[0].text, "猫")
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
        words = [t.lemma for t in sent.shallow]
        self.assertEqual(words, ['It', 'rain', '.'])


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
