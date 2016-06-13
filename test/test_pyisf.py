#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing pyisf library
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
__copyright__ = "Copyright 2015, pyisf"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
import unittest

import json

from coolisf.gold_extract import read_ace_output
from coolisf.gold_extract import sentence_to_xml
from coolisf.util import Grammar

########################################################################

TEST_SENTENCES  = 'data/bib.txt'
ACE_OUTPUT_FILE = 'data/bib.mrs.txt'

class TestPyISF(unittest.TestCase):

    def test_ace_output_to_xml(self):
        sentences = read_ace_output(ACE_OUTPUT_FILE)
        self.assertTrue(sentences)

        sent = sentences[0]
        self.assertEqual(len(sent.mrs), 3)
        
        # sentence to XML
        xml = sentence_to_xml(sent)
        self.assertTrue(xml)
        # ensure DMRS nodes count
        dmrs_nodes = xml.findall('./dmrses/dmrs')
        self.assertEqual(len(dmrs_nodes), 3)

    def test_txt_to_dmrs(self):
        print("Test parsing raw text sentences")
        ERG = Grammar()
        with open(TEST_SENTENCES) as test_file:
            raw_sentences = test_file.readlines()
            sentences = [ ERG.txt2dmrs(x) for x in raw_sentences ]
            self.assertEqual(len(sentences[0].mrs), 5)
            self.assertEqual(len(sentences[1].mrs), 5)
            self.assertEqual(len(sentences[2].mrs), 0)
            
            self.assertTrue(sentences[0].mrs[0].dmrs_xml(True))
########################################################################

def main():
    unittest.main()

if __name__ == "__main__":
    main()
