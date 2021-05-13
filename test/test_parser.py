#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing parsers
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from coolisf.model import Sentence, DMRSLayout
from coolisf.parsers.dmrs_str import parse_dmrs_str, tokenize_dmrs_str, parse_dmrs


########################################################################

def getLogger():
    return logging.getLogger(__name__)


########################################################################

class TestDMRSParser(unittest.TestCase):

    dstr = """dmrs {
  10000 [def_explicit_q<0:2> x pers=3 num=sg ind=+];
  10001 [poss<0:2> e sf=prop mood=indicative perf=- tense=untensed prog=-];
  10002 [pronoun_q<0:2> x pt=std num=sg pers=1];
  10003 [pron<0:2> x pt=std num=sg pers=1];
  10004 [_name_n_of_rel<3:7> x pers=3 num=sg ind=+];
  10005 [_be_v_id_rel<8:10> e sf=prop mood=indicative perf=- tense=pres prog=-];
  10006 [udef_q<11:20> x pers=3 num=pl ind=+];
  10007 [named<11:20>("Abraham") x pers=3 num=pl ind=+];
  0:/H -> 10005;
  10000:RSTR/H -> 10004;
  10001:ARG2/NEQ -> 10003;
  10001:ARG1/EQ -> 10004;
  10002:RSTR/H -> 10003;
  10005:ARG1/NEQ -> 10004;
  10005:ARG2/NEQ -> 10007;
  10006:RSTR/H -> 10007;
}"""
    dstr2 = """dmrs {
10000 [def_explicit_q<0:2> ];
10001 [poss<0:2> e SF=prop TENSE=untensed MOOD=indicative PROG=- PERF=-];
10002 [pronoun_q<0:2> ];
10003 [pron<0:2> x NUM=sg PERS=1];
10004 [_name_n_of<3:7> x NUM=sg PERS=3 IND=+ synsetid=06333653-n synset_lemma=name synset_score=94];
10005 [_be_v_id<8:10> e SF=prop TENSE=pres MOOD=indicative PROG=- PERF=- synsetid=02604760-v synset_lemma=be synset_score=10742];
10006 [proper_q<11:26> ];
10007 [compound<11:26> e SF=prop TENSE=untensed MOOD=indicative PROG=- PERF=-];
10008 [proper_q<11:19> ];
10009 [named<11:19>("Sherlock") x NUM=sg PERS=3 IND=+];
10010 [named<20:26>("Humere") x NUM=sg PERS=3 IND=+];
0:/H -> 10005;
10000:RSTR/H -> 10004;
10001:ARG2/NEQ -> 10003;
10001:ARG1/EQ -> 10004;
10002:RSTR/H -> 10003;
10005:ARG1/NEQ -> 10004;
10005:ARG2/NEQ -> 10010;
10006:RSTR/H -> 10010;
10007:ARG2/NEQ -> 10009;
10007:ARG1/EQ -> 10010;
10008:RSTR/H -> 10009
} """
    dstrs = (dstr, dstr2)

    def test_parse_node(self):
        for dstr in self.dstrs:
            tokens = tokenize_dmrs_str(dstr)
            dj = parse_dmrs(tokens)
            self.assertTrue(dj)

    def test_parse_str(self):
        dj = parse_dmrs_str(self.dstr2)
        dmrs = DMRSLayout(dj)
        self.assertTrue(dmrs.to_json())
        preds = [n.predstr for n in dmrs.nodes]
        expected = ['def_explicit_q', 'poss', 'pronoun_q', 'pron', '_name_n_of', '_be_v_id', 'proper_q', 'compound', 'proper_q', 'named', 'named']
        self.assertEqual(preds, expected)

    def test_dmrs_from_string(self):
        mrs = """[ TOP: h0 RELS: < [ _rain_v_1_rel<3:9> LBL: h1 ARG0: e2 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: pres ] ] > HCONS: < h0 qeq h1 > ]"""
        s = Sentence("It rains.")
        s.add(mrs)
        # now clone the added MRS via DMRS string
        dstr = s[0].dmrs().tostring()
        s.add(dmrs_str=dstr)
        self.assertEqual(s[0].mrs().tostring(), s[1].mrs().tostring())


########################################################################

if __name__ == "__main__":
    unittest.main()
