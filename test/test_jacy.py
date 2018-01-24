#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for coolisf/jacy
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
import logging

from coolisf import GrammarHub

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

txt = '雨 が 降る 。'
txt2 = '猫が好きです。'


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Test cases
# ------------------------------------------------------------------------------

class TestJacy(unittest.TestCase):

    ghub = GrammarHub()

    def test_jacy(self):
        # without mecab
        s = self.ghub.JACY.parse(txt)
        self.assertTrue(s)
        s = self.ghub.JACY.parse(txt2)
        self.assertFalse(s)
        # with mecab
        s = self.ghub.JACYMC.parse(txt)
        self.assertTrue(s)
        s = self.ghub.JACYMC.parse(txt2)
        self.assertTrue(s)
        self.assertEqual(s.text, '猫 が 好き です 。 \n')
        # test JACY/DK
        s = self.ghub.JACYDK.parse(txt, ignore_cache=True)
        getLogger().debug("shallow", s.shallow)
        for tk in s.shallow:
            getLogger().debug(tk)
        getLogger().debug(s)


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
