#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for coolisf/jacy
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

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
