#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test ERG-Wordnet mapping
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import unittest
import logging

from coolisf.ergex import read_erg_lex, find_mwe
from coolisf.mappings import PredSense
from coolisf.model import Reading, Predicate
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
        print(find_mwe())
        mwe_list = list(find_mwe())[:5]
        self.assertEqual(len(mwe_list), 5)

    def test_search_ep(self):
        r = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _of+course_a_1<0:9> LBL: h1 ARG0: i4 ARG1: h5 ]
          [ pron<10:12> LBL: h6 ARG0: x3 [ x PERS: 3 NUM: sg GEND: n PT: std ] ]
          [ pronoun_q<10:12> LBL: h7 ARG0: x3 RSTR: h8 BODY: h9 ]
          [ _work_v_1<13:19> LBL: h10 ARG0: e2 ARG1: x3 ARG2: i11 ] >
  HCONS: < h0 qeq h1 h5 qeq h10 h8 qeq h6 > ]""")
        eps = r.dmrs().obj().eps()
        p = eps[0]
        self.assertEqual(p.pred.string, '_of+course_a_1_rel')
        out = PredSense.search_ep(p)
        self.assertIn('00038625-r', out)
        # how about ``now''?
        r2 = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:2> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg GEND: n PT: std ] ]
          [ pronoun_q<0:2> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _work_v_1<3:8> LBL: h1 ARG0: e2 ARG1: x3 ARG2: i8 ]
          [ loc_nonsp<9:13> LBL: h1 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e2 ARG2: x10 [ x PERS: 3 NUM: sg ] ]
          [ time_n<9:13> LBL: h11 ARG0: x10 ]
          [ def_implicit_q<9:13> LBL: h12 ARG0: x10 RSTR: h13 BODY: h14 ]
          [ _now_a_1<9:13> LBL: h11 ARG0: e15 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x10 ] >
        HCONS: < h0 qeq h1 h6 qeq h4 h13 qeq h11 > ]""")
        p = r2.dmrs().obj().eps()[-1]
        out = PredSense.search_ep(p)
        for ss in out:
            self.assertEqual(ss.lemma, 'now')
            self.assertEqual(ss.ID.pos, 'r')

    def test_pred_type(self):
        p = Predicate.from_string('idiom_q_i')
        self.assertEqual(p.ptype, Predicate.GRAMMARPRED)
        self.assertEqual(p.to_pred().type, Predicate.GRAMMARPRED)
        p = Predicate.from_string('_dog_n_1')
        self.assertEqual(p.ptype, Predicate.STRINGPRED)
        self.assertEqual(p.to_pred().type, Predicate.STRINGPRED)

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

    def test_get_pred_pos(self):
        r = Reading("""[ TOP: h0 INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] RELS: < [ pron<0:1> LBL: h4 ARG0: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ] [ pronoun_q<0:1> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ] [ _happy_a_with<5:11> LBL: h1 ARG0: e2 ARG1: x3 ARG2: i8 ] > HCONS: < h0 qeq h1 h6 qeq h4 > ]""")
        actual = r.dmrs().tokenize_pos()
        expected = [('pron', 'x', 0, 1), ('pronoun', 'x', 0, 1), ('happy', 'a', 5, 11)]
        self.assertEqual(actual, expected)

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

    def test_ignored(self):
        ss = PredSense.search_pred_string('card_rel')
        self.assertFalse(ss)
        ss = PredSense.search_pred_string('card')
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
        d = list(PredSense.search_pred_string('_green+tea_n_1'))
        self.assertEqual(d[0].synsetid, '07935152-n')

    def test_search_node(self):
        mrs = """[ TOP: h0 RELS: < [ proper_q<0:4> LBL: h1 ARG0: x6 [ x NUM: sg PERS: 3 GEND: m IND: + ] RSTR: h10 ] [ named<0:4> LBL: h2 ARG0: x6 CARG: "John" ] [ _have_v_1<5:8> LBL: h3 ARG0: e7 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x6 ARG2: x9 [ x NUM: sg PERS: 3 IND: + ] ] [ udef_q<9:10> LBL: h4 ARG0: x9 RSTR: h11 ] [ card<9:10> LBL: h5 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x9 CARG: "1" ] [ _car_n_1<11:15> LBL: h5 ARG0: x9 ] > HCONS: < h0 qeq h3 h10 qeq h2 h11 qeq h5 > ]"""
        r = Reading(mrs)
        print(r.dmrs().preds())
        eps = list(r.dmrs().get_lexical_preds())
        for ep in eps:
            print(ep.pred.string, PredSense.search_ep(ep))
        proper_q, _have_v_1, udef_q, card, _car_n_1 = eps
        self.assertFalse(PredSense.search_ep(proper_q))
        self.assertTrue(PredSense.search_ep(_have_v_1))
        self.assertFalse(PredSense.search_ep(udef_q))
        self.assertTrue(PredSense.search_ep(_car_n_1))
        # TODO: Fix card mapping


########################################################################

if __name__ == "__main__":
    unittest.main()
