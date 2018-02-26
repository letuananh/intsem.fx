#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test ERG-Wordnet mapping
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

import os
import unittest
import logging

from coolisf.ergex import read_erg_lex, find_mwe
from coolisf.mappings import PredSense
from coolisf.model import Predicate
from coolisf import GrammarHub

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

from test import TEST_DATA
TEST_SENTENCES = os.path.join(TEST_DATA, 'bib.txt')
ACE_OUTPUT_FILE = os.path.join(TEST_DATA, 'bib.mrs.txt')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# TEST SCRIPTS
# ------------------------------------------------------------------------------

class TestMain(unittest.TestCase):

    lexdb = read_erg_lex()
    ERG = GrammarHub().ERG

    def test_find_mwe(self):
        mwe_list = list(find_mwe())[:5]
        self.assertEqual(len(mwe_list), 5)

    def test_read_erg_lexdb(self):
        # get non empty rels
        nonempty = [x for x in self.lexdb if x.keyrel != '\\N']
        self.assertGreater(len(nonempty), 30000)
        for l in self.lexdb:
            self.assertTrue(l.lextype)

    def test_erg2wn(self):
        d = PredSense.search_pred_string('_test_v_1')
        self.assertEqual({str(x.synsetid) for x in d}, {'02531625-v', '02533109-v', '00786458-v', '02745713-v', '01112584-v', '00920778-v', '00669970-v'})
        pass

    def test_extend_lemma(self):
        self.assertEqual(PredSense.extend_lemma('night bird'), {'night-bird', 'night bird', 'nightbird'})
        self.assertEqual(PredSense.extend_lemma('above+all'), {'above-all', 'above+all', 'aboveall', 'above all'})
        predstrs = ['_independently+of_p', '_with+respect+to_p', '_counter+to_p', '_such+as_p', '_nomore_a_1']
        preds = [Predicate.from_string(p) for p in predstrs]
        for p in preds:
            lemmas = PredSense.extend_lemma(p.lemma)
            getLogger().debug("{}: {}".format(p, lemmas))
            self.assertTrue(lemmas)

    def test_lemma_searching(self):
        ss = PredSense.search_sense({'above all'}, 'r')
        self.assertEqual({'00150671-r', '00158190-r'}, {s.ID for s in ss})

    def test_special_preds(self):
        self.assertFalse(PredSense.search_pred_string('a_q'))
        self.assertFalse(PredSense.search_pred_string('named_rel'))
        self.assertFalse(PredSense.search_pred(Predicate.from_string('named_rel').to_pred()))
        self.assertFalse(PredSense.search_pred(Predicate.from_string('_a_q_rel').to_pred()))
        self.assertTrue(PredSense.search_pred_string('neg_rel'))
        self.assertTrue(PredSense.search_pred_string('neg'))

    def test_x_deg(self):
        ss = PredSense.search_pred_string('_well_x_deg')
        print(ss)
        for s in ss:
            self.assertIn(s.ID.pos, 'ar')

    def test_subord(self):
        ss = PredSense.search_pred_string('_as_x_subord')
        self.assertFalse(ss)

    def test_time(self):
        ss = PredSense.search_pred_string('_time_n_of_rel')
        self.assertTrue(ss)
        ss = PredSense.search_pred_string('time_n_rel')
        self.assertFalse(ss)

    def test_mwe_lemma_sense(self):
        ss = PredSense.search_pred_string('_squeeze_v_in')
        getLogger().debug(ss)

    def test_unknown_preds(self):
        preds = ['_ventilator/NN_u_unknown', '_stepfather/NN_u_unknown',
                 '_soothingly/RB_u_unknown', '_dissolute/JJ_u_unknown']
        for pred in preds:
            ss = PredSense.search_pred_string(pred)
            self.assertTrue(bool(pred.startswith('_')) != bool(not ss))
            getLogger().debug("Candidates for {}: {}".format(pred, ss))

    def test_known_gpreds(self):
        preds = ['_be_v_id_rel', 'person_rel', 'person_n_rel', '_person_n_1', 'pronoun_q']
        for pred in preds:
            ss = PredSense.search_pred_string(pred)
            self.assertTrue(bool(pred.startswith('_')) != bool(not ss))
            getLogger().debug("Candidates for {}: {}".format(pred, ss))

    def test_known_concepts(self):
        ctx = PredSense.wn.ctx()
        # test verb
        synsets = PredSense.search_pred_string('_bark_v_1', ctx=ctx)
        self.assertTrue(synsets)
        for synset in synsets:
            self.assertEqual(synset.ID.pos, 'v')
            self.assertIn('bark', synset.lemmas)
        # test noun
        synsets = PredSense.search_pred_string('_bark_n_1', ctx=ctx)
        self.assertTrue(synsets)
        for synset in synsets:
            self.assertEqual(synset.ID.pos, 'n')
            self.assertIn('bark', synset.lemmas)
        # test adj
        synsets = PredSense.search_pred_string('_quick_a_1', ctx=ctx)
        self.assertTrue(synsets)
        for synset in synsets:
            self.assertEqual(synset.ID.pos, 'a')
            self.assertIn('quick', synset.lemmas)
        # MWE
        synsets = PredSense.search_pred_string('_look_v_up', ctx=ctx)
        for synset in synsets:
            self.assertIn("look up", synset.lemmas)
        synsets = PredSense.search_pred_string('_above+all_a_1_rel', ctx=ctx)
        getLogger().debug("above+all: {}".format(synsets))
        for synset in synsets:
            self.assertIn('above all', synset.lemmas)
        self.assertTrue(synsets)
        preds = ["_above-mentioned_a_1_rel", "_allright_a_for_rel", "_abrasive_a_1_rel",
                 "_squeak_n_1_rel", "_abbreviation_n_1_rel", "_abandon_n_1_rel", "_bitter_a_1_rel",
                 '"_abbreviate_v_1_rel"', '"_acrolect_n_1_rel"', '_co-opt_v_1_rel']
        for p in preds:
            ss = PredSense.search_pred_string(p, ctx=ctx)
            getLogger().debug("{}: {}".format(p, ss))
        ctx.close()

    def test_known_mwe(self):
        d = PredSense.search_pred_string('_green+tea_n_1')
        self.assertEqual(d[0].synsetid, '07935152-n')


########################################################################

if __name__ == "__main__":
    unittest.main()
