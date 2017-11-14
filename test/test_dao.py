#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test DAO
Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
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
__copyright__ = "Copyright 2017, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import logging
import unittest

from chirptext import header

from coolisf import GrammarHub
from coolisf.dao import read_tsdb, CorpusDAOSQLite
from coolisf.dao.ruledb import LexRuleDB, parse_lexunit
from coolisf.model import Document, LexUnit, RuleInfo

# -----------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEST_DATA = os.path.join(os.path.dirname(__file__), 'data')


# -----------------------------------------------------------------------
# TEST SCRIPTS
# -----------------------------------------------------------------------

class TestTSDBDAO(unittest.TestCase):

    def test_read_tsdb(self):
        doc = read_tsdb('data/gold')
        self.assertTrue(doc)
        self.assertTrue(len(doc))


class TestRuleDB(unittest.TestCase):

    ghub = GrammarHub()
    rdb = LexRuleDB(':memory:')

    def get_constructions(self):
        return [LexUnit(lemma='emergence', pos='n', synsetid='00044455-n'),
                LexUnit(lemma='green tea', pos='n', synsetid='07935152-n'),
                LexUnit(lemma='look up', pos='v', synsetid='00877083-v'),
                LexUnit(lemma='emergent', pos='a', synsetid='00003553-a'),
                LexUnit(lemma='quickly', pos='r', synsetid='00085811-r')]

    def test_add_lexunit(self):
        lu = LexUnit(lemma='emergence', pos='n', synsetid='00044455-n')
        with self.rdb.ctx() as ctx:
            lu.ID = ctx.lexunit.save(lu)
            self.rdb.flag(lu, LexUnit.GOLD, ctx=ctx)

    def test_add_stuff(self):
        constructions = self.get_constructions()
        with self.rdb.ctx() as ctx:
            # generate rules
            self.rdb.generate_rules(constructions, lambda x: parse_lexunit(x, self.ghub.ERG), ctx=ctx)
            # generate rule head
            for lu in ctx.lexunit.select():
                self.rdb.get_lexunit(lu, ctx=ctx)
                for r in lu.parses:
                    head = r.dmrs().layout.head()
                    if head is not None:
                        rinfo = RuleInfo(lu.ID, r.ID, head.predstr)
                        self.rdb.ruleinfo.save(rinfo, ctx=ctx)
            # verification
            tea_rules = self.rdb.find_rule('_tea_n_1', ctx=ctx)
            self.assertTrue(len(tea_rules))
            for rinfo in tea_rules:
                self.assertTrue(rinfo.lid)
                self.assertTrue(rinfo.rid)
                self.assertEqual(rinfo.pred, '_tea_n_1')
                rule = self.rdb.get_rule(rinfo.lid, rinfo.rid, ctx=ctx)
                self.assertEqual(len(rule), 1)
            for c in constructions:
                lus = self.rdb.find_lexunits(lemma=c.lemma, ctx=ctx)
                self.assertEqual(len(lus), 1)
                lu = lus[0]
                self.rdb.get_lexunit(lu, ctx=ctx)
                self.assertEqual(lu.lemma, c.lemma)
                self.assertTrue(len(lu.parses))
                self.assertTrue(lu.parses.docID)
                # test select a specific reading
                rule = self.rdb.get_rule(lu.ID, lu[0].ID, ctx=ctx)
                self.assertEqual(len(rule), 1)

    def test_get_rule(self):
        rdb = LexRuleDB(':memory:')
        with rdb.ctx() as ctx:
            # generate rules
            rdb.generate_rules(self.get_constructions(), lambda x: parse_lexunit(x, self.ghub.ERG), ctx=ctx)
            all_lus = ctx.lexunit.select()
            for l in all_lus:
                print(l)
            lu = ctx.lexunit.select_single('lemma=?', ('green tea',))
            self.assertIsNotNone(lu)
            rdb.get_lexunit(lu, ctx=ctx)
            lid, rid = (lu.ID, lu[0].ID)  # rule ID = (lid, rid)
            rule = self.rdb.get_rule(lid, rid, ctx=ctx)
            print(rule[0])


########################################################################

if __name__ == "__main__":
    unittest.main()
