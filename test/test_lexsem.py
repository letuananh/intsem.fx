#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing lexem module
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
import logging

from chirptext import texttaglib as ttl
from coolisf import GrammarHub


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestLexsem(unittest.TestCase):

    ghub = GrammarHub()

    def test_wsd(self):
        s = self.ghub.parse("John gives Mary a book.", "ERG_ISF", tagger=ttl.Tag.MFS, ignore_cache=True)
        getLogger().debug("Sentence: {}".format(s))
        self.assertTrue(s)
        self.assertTrue(len(s))

    def test_neg(self):
        s = self.ghub.parse("Certainly not.", "ERG_ISF", tagger=ttl.Tag.MFS, ignore_cache=True)
        getLogger().debug(s[0].dmrs().tags)


########################################################################

if __name__ == "__main__":
    unittest.main()
