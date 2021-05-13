#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing lexem module
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from texttaglib.chirptext import texttaglib as ttl
from coolisf import GrammarHub
from coolisf.model import Document, Sentence, Predicate
from coolisf.lexsem import Lexsem, import_shallow, taggable_eps
from coolisf.mappings import PredSense


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

TEST_MRS = """[ TOP: h0
  RELS: < [ pron_rel<0:1> LBL: h1 ARG0: x20 [ x IND: + NUM: sg PERS: 1 PT: std ] ]
          [ pronoun_q_rel<0:1> LBL: h2 ARG0: x20 RSTR: h37 ]
          [ _send_v_1_rel<2:6> LBL: h3 ARG0: e21 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: past ] ARG1: x20 ARG2: x23 [ x IND: + NUM: pl PERS: 3 ] ARG3: h38 ]
          [ udef_q_rel<7:27> LBL: h4 ARG0: x23 RSTR: h39 ]
          [ _chatty/JJ_u_unknown_rel<7:13> LBL: h5 ARG0: e22 [ e MOOD: indicative PERF: - PROG: bool SF: prop TENSE: untensed ] ARG1: x23 ]
          [ _announcement_n_of_rel<14:27> LBL: h5 ARG0: x23 ]
          [ _to_p_rel<28:30> LBL: h6 ARG0: e24 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: x23 ARG2: x27 [ x IND: + NUM: sg PERS: 3 ] ]
          [ _the_q_rel<31:34> LBL: h7 ARG0: x27 RSTR: h40 ]
          [ compound_rel<35:44> LBL: h8 ARG0: e25 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: x27 ARG2: x26 [ x IND: - NUM: sg PERS: 3 PT: notpro ] ]
          [ udef_q_rel<35:39> LBL: h9 ARG0: x26 RSTR: h41 ]
          [ _beta_n_1_rel<35:39> LBL: h10 ARG0: x26 ]
          [ _list_n_of_rel<40:44> LBL: h8 ARG0: x27 ]
          [ loc_nonsp_rel<45:65> LBL: h3 ARG0: e28 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: e21 ARG2: x29 [ x NUM: sg PERS: 3 ] ]
          [ free_relative_ever_q_rel<45:53> LBL: h11 ARG0: x29 RSTR: h42 ]
          [ temp_rel<45:53> LBL: h12 ARG0: x29 ]
          [ temp_loc_x_rel<45:53> LBL: h12 ARG0: e30 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: e32 [ e MOOD: indicative SF: prop TENSE: past ] ARG2: x29 ]
          [ pron_rel<54:55> LBL: h13 ARG0: x31 [ x IND: + NUM: sg PERS: 1 PT: std ] ]
          [ pronoun_q_rel<54:55> LBL: h14 ARG0: x31 RSTR: h43 ]
          [ _release_v_1_rel<56:65> LBL: h12 ARG0: e32 ARG1: x31 ]
          [ subord_rel<66:100> LBL: h15 ARG0: e33 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: h44 ARG2: h45 ]
          [ _encourage_v_1_rel<66:77> LBL: h16 ARG0: e34 [ e MOOD: indicative PERF: - PROG: + SF: prop TENSE: untensed ] ARG2: x35 [ x IND: + NUM: pl PERS: 3 ] ARG3: h46 ]
          [ udef_q_rel<78:84> LBL: h17 ARG0: x35 RSTR: h47 ]
          [ _people_n_of_rel<78:84> LBL: h18 ARG0: x35 ]
          [ _participate_v_in_rel<88:100> LBL: h19 ARG0: e36 [ e MOOD: indicative PERF: - PROG: - SF: prop-or-ques TENSE: untensed ] ARG1: x35 ] >
  HCONS: < h0 qeq h15 h37 qeq h1 h38 qeq h6 h39 qeq h5 h40 qeq h8 h41 qeq h10 h42 qeq h12 h43 qeq h13 h44 qeq h3 h45 qeq h16 h46 qeq h19 h47 qeq h18 > ]"""


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestLexsem(unittest.TestCase):

    ghub = GrammarHub()

    def test_mapping(self):
        s = Sentence("I sent chatty announcements to the beta list whenever I released, encouraging people to participate.")
        s.add(TEST_MRS)
        eps = taggable_eps(s[0].dmrs().obj().eps(), mode=Lexsem.NAIVE)
        eps = sorted(eps, key=lambda x: (x.cfrom, x.cto, x.pred.type, x.pred.pos == 'q'))
        actual = [str(ep.pred) for ep in eps]
        expected = ['pron_rel', 'pronoun_q_rel', '_send_v_1_rel', '_chatty/JJ_u_unknown_rel', 'udef_q_rel', '_announcement_n_of_rel', '_to_p_rel', '_the_q_rel', 'udef_q_rel', '_beta_n_1_rel', 'compound_rel', '_list_n_of_rel', 'temp_rel', 'temp_loc_x_rel', 'free_relative_ever_q_rel', 'loc_nonsp_rel', 'pron_rel', 'pronoun_q_rel', '_release_v_1_rel', '_encourage_v_1_rel', 'subord_rel', 'udef_q_rel', '_people_n_of_rel', '_participate_v_in_rel']
        self.assertEqual(actual, expected)

    def test_matching_instead_of(self):
        txt = 'I ate cakes instead of pies .'
        s = self.ghub.parse(txt, 'ERG', tagger=None, pc=1, ignore_cache=True)
        sttl = ttl.Sentence(txt)
        sttl.tokens = 'I ate cakes instead of pies .'.split()
        sttl.new_concept('00098714-r', clemma='instead', tokens=[3])
        s.shallow = sttl
        res = import_shallow(s)
        print(res)

    def test_wsd(self):
        s = self.ghub.parse("John gives Mary a book.", "ERG_ISF", tagger=ttl.Tag.MFS, ignore_cache=True)
        getLogger().debug("Sentence: {}".format(s))
        self.assertTrue(s)
        self.assertTrue(len(s))

    def test_modal_verb(self):
        p = Predicate.from_string('_must_v_modal')
        self.assertEqual((p.lemma, p.pos, p.sense), ('must', 'v', 'modal'))
        ss = PredSense.search_pred_string('_must_v_modal')
        self.assertFalse(len(ss))

    def test_neg(self):
        s = self.ghub.parse("Certainly not.", "ERG_ISF", tagger=ttl.Tag.MFS, ignore_cache=True)
        getLogger().debug(s[0].dmrs().tags)


########################################################################

if __name__ == "__main__":
    unittest.main()
