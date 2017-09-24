#!/Usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing parsers
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, coolisf"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import unittest
import logging

from coolisf.model import Sentence, Reading, DMRSLayout
from coolisf.parsers.dmrs_str import parse_dmrs_str, tokenize_dmrs_str, parse_dmrs


########################################################################

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Change this to DEBUG for more information

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')


########################################################################

class TestDMRSParser(unittest.TestCase):

    dstr = '''dmrs {
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
}'''
    dstr2 = '''dmrs {
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
} '''
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
        mrs = '''[ TOP: h0 RELS: < [ _rain_v_1_rel<3:9> LBL: h1 ARG0: e2 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: pres ] ] > HCONS: < h0 qeq h1 > ]'''
        s = Sentence("It rains.")
        s.add(mrs)
        # now clone the added MRS via DMRS string
        dstr = s[0].dmrs().tostring()
        s.add(dmrs_str=dstr)
        self.assertEqual(s[0].mrs().tostring(), s[1].mrs().tostring())


########################################################################

if __name__ == "__main__":
    unittest.main()
