#!/Usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing coolisf models
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
__copyright__ = "Copyright 2017, coolisf"
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

from chirptext import header
from chirptext.texttaglib import TagInfo

from coolisf import GrammarHub
from coolisf.util import is_valid_name, sent2json
from coolisf.model import Corpus, Document, Sentence, Reading
from coolisf.model import DMRSLayout, Node, Link

# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Change this to DEBUG for more information

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestGrammarHub(unittest.TestCase):

    ghub = GrammarHub()
    EI = ghub.ERG_ISF

    def test_sent(self):
        header("Test model")
        doc = Document("test")
        s = doc.new("It rains.")
        s.add('''[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]''')
        # test full work flow:
        #   mrs_str > dmrs() > xml > layout > dmrs > mrs > mrs_str
        expected = '''[ TOP: h0 RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ] > HCONS: < h0 qeq h1 > ]'''
        actual = DMRSLayout.from_xml(s[0].edit().to_dmrs().xml()).to_dmrs().to_mrs().tostring(False)
        self.assertEqual(actual, expected)
        # Test different formats
        xstr = s.to_xml_str()
        self.assertTrue(xstr)
        lts = s.to_latex()  # LaTeX scripts
        self.assertTrue(lts)

    def test_convert(self):
        print("Test convert DMRSLayout to and from XML")
        dmrs = Reading('''[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]''').dmrs()
        layout = DMRSLayout.from_xml(dmrs.xml())
        self.assertEqual(dmrs.layout.to_json(), layout.to_json())

    def test_dmrs(self):
        header("Test building a DMRS from scratch")
        corpus = Corpus(name="manual")
        doc = corpus.new(name="testdoc")
        sent = doc.new("It rains.")
        self.assertIsInstance(sent, Sentence)
        reading = sent.add('[]')
        dmrs = reading.dmrs()
        l = dmrs.layout
        n = Node(10000, "_rain_v_1", 3, 9)
        n.sortinfo.update({'sf': 'prop', 'tense': 'pres', 'mood': 'indicative',
                           'prog': '-', 'perf': '-', 'sarcasm': '-'})
        l.add_node(n)
        l.add_link(Link(0, 10000, '', 'H'))  # this is top
        l.save()
        # sense tag the DMRS
        sent.tag(TagInfo.MFS)
        self.assertGreaterEqual(len(dmrs.tags), 1)
        self.assertTrue(sent.to_xml_str())

    def test_to_latex(self):
        dmrs = Reading('''[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]''').dmrs()
        print(dmrs.latex())

    def test_sent2json(self):
        sent = Sentence('It rains.')
        sent.add('''[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]''')
        j = sent2json(sent)
        print(j)


class TestDMRSModel(unittest.TestCase):

    def test_node(self):
        n = Node()
        n.rplemma = "foo"
        n.rppos = "n"
        n.rpsense = "1"
        print(n)


class TestName(unittest.TestCase):

    def test_valid_name(self):
        self.assertTrue(is_valid_name('test'))
        self.assertTrue(is_valid_name('test123'))
        self.assertTrue(is_valid_name('1'))
        self.assertTrue(is_valid_name('1234'))
        self.assertTrue(is_valid_name('12_34'))
        self.assertTrue(is_valid_name('ABC12_34'))
        # invalid names
        self.assertFalse(is_valid_name(''))
        self.assertFalse(is_valid_name(None))
        self.assertFalse(is_valid_name('a.b'))


########################################################################

if __name__ == "__main__":
    unittest.main()
