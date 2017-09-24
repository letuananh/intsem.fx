#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for ghub
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
__copyright__ = "Copyright 2017, intsem.fx"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import unittest

from coolisf import GrammarHub
from coolisf.dao import CorpusDAOSQLite

# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestVirgo(unittest.TestCase):

    db = CorpusDAOSQLite(":memory:", "memdb")
    ghub = GrammarHub()

    def test_erg(self):
        db = self.db
        with self.db.ctx() as ctx:
            # create sample sentence
            corpus = db.create_corpus('test', ctx=ctx)
            doc = corpus.new('testdoc')
            db.save_doc(doc, ctx=ctx)
            s = self.ghub.ERG.parse("It works.", parse_count=1)
            j1 = s[0].dmrs().json()
            s.docID = doc.ID
            db.save_sent(s, ctx=ctx)
            # select back
            sent = db.get_sent(s.ID, ctx=ctx)
            j2 = sent[0].dmrs().json()
            self.assertEqual(j1, j2)

    def test_ghub_to_corpus(self):
        db = self.db
        with self.db.ctx() as ctx:
            # create sample sentence
            corpus = db.create_corpus('test', ctx=ctx)
            doc = corpus.new('testdoc')
            db.save_doc(doc, ctx=ctx)
            s = self.ghub.parse("Abraham's dog barked.", "ERG", pc=1)
            s.docID = doc.ID
            db.save_sent(s, ctx=ctx)
            # select back
            sent = db.get_sent(s.ID, ctx=ctx)
            print(sent[0])


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
