#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for coolisf/virgo
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from coolisf import GrammarHub


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestVirgo(unittest.TestCase):

    ghub = GrammarHub()

    def test_virgo(self):
        s = self.ghub.VRG.parse("chim bay.")
        actual = [n.predstr for n in s.edit(0).nodes]
        expected = ['_chim_n', 'exist_q', '_bay_v']
        self.assertEqual(actual, expected)


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
