#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing ISF tools
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from texttaglib.chirptext import texttaglib as ttl
from coolisf import read_config
from coolisf import GrammarHub
from coolisf.common import overlap, tags_to_concepts


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


samples = ['猫が好きです。',
           'ケーキを食べた。',
           '雨が降る。']
NEKO = '02121620-n'
SUKI = '01292683-a'
KEKI = '07628870-n'
TABERU = '01168468-v'
AME = '15008607-n'
FURU = '02756821-v'


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestConfigReader(unittest.TestCase):

    def test_config(self):
        cfg = read_config()
        self.assertTrue(cfg)


class TestTools(unittest.TestCase):

    ghub = GrammarHub()

    def test_overlap(self):
        self.assertTrue(overlap(0, 3, 2, 4))
        self.assertTrue(overlap(2, 4, 0, 3))
        self.assertTrue(overlap(2, 6, 3, 4))
        self.assertTrue(overlap(3, 4, 2, 6))
        self.assertTrue(overlap(3, 4, 3, 4))
        self.assertFalse(overlap(2, 4, 0, 2))
        self.assertFalse(overlap(0, 2, 2, 4))
        self.assertFalse(overlap(1, 2, 3, 4))
        self.assertFalse(overlap(3, 4, 1, 2))
        self.assertRaises(ValueError, lambda: overlap(None, 4, 1, 2))

    def test_tag_to_concepts(self):
        doc_ttl = ttl.Document('test', 'data')
        for ID, txt in enumerate(samples):
            s = self.ghub.JACYDK.parse(txt, ignore_cache=True)
            sent_ttl = s.shallow
            sent_ttl.ID = ID + 1
            doc_ttl.add_sent(s.shallow)
        # create tags at sentence level
        doc_ttl[0].new_tag(NEKO, 0, 1, tagtype='WN')
        doc_ttl[0].new_tag(SUKI, 2, 4, tagtype='WN')
        doc_ttl[1].new_tag(KEKI, 0, 3, tagtype='WN')
        doc_ttl[1].new_tag(TABERU, 4, 7, tagtype='WN')
        doc_ttl[2].new_tag(AME, 0, 1, tagtype='WN')
        doc_ttl[2].new_tag(FURU, 2, 4, tagtype='WN')
        # Try to map the concepts to tokens
        for s in doc_ttl:
            getLogger().debug("Sentence: {} - {} - {}".format(s, s.tokens, s.tags))
            tags_to_concepts(s)
            for c in s.concepts:
                getLogger().debug(c)
            self.assertEquals(len(s.tags), len(s.concepts))
        doc_ttl.write_ttl()


########################################################################

if __name__ == "__main__":
    unittest.main()
