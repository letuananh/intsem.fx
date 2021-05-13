#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for mining script
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from texttaglib.chirptext import header
from yawlib import YLConfig
from yawlib.omwsql import OMWSQL

import miner
from coolisf import GrammarHub
from coolisf.model import LexUnit, Reading, RuleInfo
from coolisf.morph import Transformer

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

TEST_GOLD_DIR = 'data'
ghub = GrammarHub()
ERG = ghub.ERG
wn = OMWSQL(YLConfig.OMW_DB)


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# DATA STRUCTURES
# ------------------------------------------------------------------------------

class TestMiningPred(unittest.TestCase):

    db = Transformer().rdb

    def test_parsing(self):
        ghub = GrammarHub()
        # noun
        sent = ghub.ERG.parse('dog', extra_args=['-r', 'root_wn_n'])
        self.assertGreater(len(sent), 0)
        dmrs = sent[0].dmrs().obj()
        eps = dmrs.eps()
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].pred.pos, 'n')
        # verb
        sent = ghub.ERG.parse('love', extra_args=['-r', 'root_wn_v'])
        self.assertGreater(len(sent), 0)
        dmrs = sent[0].dmrs().obj()
        eps = dmrs.eps()
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].pred.pos, 'v')
        # adjective
        sent = ghub.ERG.parse('nice', extra_args=['-r', 'root_wn_adj'])
        self.assertGreater(len(sent), 0)
        dmrs = sent[0].dmrs().obj()
        eps = dmrs.eps()
        print(sent[0].mrs())
        self.assertEqual(len(eps), 1)
        self.assertEqual(eps[0].pred.pos, 'a')
        # test iterative parsing
        words = ['drink', 'eat', 'eat', 'drink']
        for parses in ghub.ERG.parse_many_iterative(words, extra_args=['-r', 'root_frag'], ignore_cache=True):
            header(parses)
            for p in parses:
                print(p.mrs())

    def test_parse_word(self):
        s = ERG.parse('burp')
        dmrs = s[0].dmrs().layout
        head = dmrs.top['ARG']
        self.assertEqual(head.pred.lemma, 'burp/NN')
        self.assertEqual(head.pred.pos, 'u')
        self.assertEqual(head.pred.sense, 'unknown')

    def test_mining(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(lemma="water ski", pos="v", limit=10, lazy=True, ctx=ctx)
            self.assertTrue(lus)
            self.assertTrue(lus[0][0].dmrs())

    def test_compound(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits('night bird', lazy=True, ctx=ctx)
            self.assertTrue(len(lus))
            lu = lus[0]
            rule = self.db.get_rule(lu.ID, lu[0].ID, ctx=ctx)
            self.assertIsNotNone(rule)
            self.assertEqual(len(rule), 1)

    def mark_unknown_words(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, ctx=ctx)
            for lu in lus[:50]:
                self.db.get_lexunit(lu, ctx=ctx)
                miner.mark_unknown_words(lu, ctx)

    def add_comment(self):
        miner.add_comment(self.db, wn, limit=50)

    def find_compounds(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, ctx=ctx)
            for lu in lus[:50]:
                self.db.get_lexunit(lu, ctx=ctx)
                miner.mark_compounds(lu, ctx)

    def find_entry(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(lemma="able", lazy=True, ctx=ctx)
            for lu in lus[:50]:
                self.db.get_lexunit(lu, mode=Reading.ACTIVE, ctx=ctx)
                dump(lu)
                self.db.get_lexunit(lu, mode=None, ctx=ctx)
                dump(lu)

    def list_entry(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, ctx=ctx)
            for lu in lus:
                self.db.get_lexunit(lu, ctx=ctx)
                print(lu)
                # dump(lu)

    def test_gold_rules(self):
        s = ERG.parse('smash', extra_args=['-r', 'root_wn_v'])
        for r in s:
            print(r)

    def mark_noun_concepts(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, pos='n', ctx=ctx)
            for lu in lus[:50]:
                self.db.get_lexunit(lu, ctx=ctx)
                miner.mark_noun_concept(lu, ctx)

    def mark_adj_concepts(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, pos='a', ctx=ctx)
            for lu in lus[:50]:
                self.db.get_lexunit(lu, ctx=ctx)
                header(lu)
                mark_adj_concepts(lu, ctx)

    def mark_verb_concepts(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, pos='v', ctx=ctx)
            for lu in lus:
                # header(lu)
                self.db.get_lexunit(lu, ctx=ctx)
                mark_verb_concepts(lu, ctx)

    def mark_adv_concepts(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(flag=LexUnit.PROCESSED, pos='r', ctx=ctx)
            for lu in lus:
                self.db.get_lexunit(lu, ctx=ctx)
                mark_adv_concepts(lu, ctx)

    def generate_rule_head(self):
        with self.db.ctx() as ctx:
            lus = self.db.find_lexunits(ctx=ctx)
            for lu in lus:
                if lu.flag not in (LexUnit.ERROR, LexUnit.PROCESSED):
                    self.db.get_lexunit(lu, ctx=ctx)
                    for r in lu:
                        if r is None:
                            print("WARNING: {}".format(lu))
                        layout = r.dmrs().layout
                        head = layout.head()
                        if head is not None and r.mode != 0:
                            rinfo = RuleInfo(lu.ID, r.ID, head.predstr)
                            print("Saving {}".format(rinfo))
                            ctx.ruleinfo.save(rinfo)
                            # print(head.predstr, lu.ID, r.ID, r.mode)

    def fix_rule_head(self):
        with self.db.ctx() as ctx:
            rsigs = ctx.ruleinfo.select('flag = ?', (RuleInfo.COMPOUND,), limit=50)
            for rsig in rsigs:
                rule = self.db.get_rule(rsig.lid, rsig.rid, ctx=ctx)
                nodes = [n for n in rule[0].dmrs().layout.nodes if n.predstr not in ('unknown', 'udef_q')]
                if len(nodes) == 1:
                    rsig.flag = RuleInfo.SINGLE_PRED
                    self.db.flag_rule(rsig.lid, rsig.rid, RuleInfo.SINGLE_PRED, ctx=ctx)
                elif len(nodes) > 1:
                    rsig.flag = RuleInfo.COMPOUND
                    self.db.flag_rule(rsig.lid, rsig.rid, RuleInfo.COMPOUND, ctx=ctx)
            # print(rsigs)


def mark_adv_concepts(lu, ctx):
    if lu.pos != 'r':
        return False
    advs = []
    almost = []
    errors = []
    for r in lu:
        layout = r.dmrs().layout
        head = layout.head()
        if head is None:
            errors.append(r)
        elif head.rppos == 'a':
            advs.append(r)
        elif head.predstr == 'unknown' and len(layout.nodes) == 2 and layout.nodes[1].rppos == 'a':
            # need to modify
            layout.delete(head)  # delete head
            layout.save()
            ctx.schema.update_reading(r, ctx=ctx)
            almost.append(r)
        else:
            errors.append(r)
    if advs:
        ctx.schema.flag(lu, LexUnit.ADV, ctx=ctx)
        miner.activate(*advs, ctx=ctx)
        miner.deactivate(*almost, ctx=ctx)
    elif almost:
        ctx.schema.flag(lu, LexUnit.ADV, ctx=ctx)
        miner.activate(*almost, ctx=ctx)
    else:
        ctx.schema.flag(lu, LexUnit.MISMATCHED, ctx=ctx)
    miner.deactivate(*errors, ctx=ctx)


def mark_verb_concepts(lu, ctx):
    if lu.pos != 'v':
        return False
    verbs = []
    # derivatives = []
    errors = []
    for r in lu:
        layout = r.dmrs().layout
        head = layout.head()
        if head is None:
            errors.append(r)
        elif head.rppos == 'v':
            verbs.append(r)
        else:
            errors.append(r)
    if verbs:
        ctx.schema.flag(lu, LexUnit.VERB, ctx=ctx)
        miner.activate(*verbs, ctx=ctx)
        miner.deactivate(*errors, ctx=ctx)


def mark_adj_concepts(lu, ctx):
    if lu.pos != 'a':
        return False
    adjs = []
    derivatives = []
    errors = []
    for r in lu:
        layout = r.dmrs().layout
        head = layout.head()
        if head is None:
            errors.append(r)
        elif head.pred.pos == 'a':
            adjs.append(r)
        elif (head.rppos == 'v' and (head.sortinfo.prog == '+' or head.sortinfo.perf == '+' or head.sortinfo.tense == 'past')):
            derivatives.append(r)
        else:
            errors.append(r)
    if adjs:
        # mark all adjs as active and anything else as inactives
        ctx.schema.flag(lu, LexUnit.ADJ, ctx=ctx)
        miner.activate(*adjs, ctx=ctx)
        miner.deactivate(*derivatives, ctx=ctx)
        miner.deactivate(*errors, ctx=ctx)
    elif derivatives:
        ctx.schema.flag(lu, LexUnit.ADJ, ctx=ctx)
        miner.activate(*derivatives, ctx=ctx)
        miner.deactivate(*errors, ctx=ctx)
    else:
        # ctx.schema.flag(lu, LexUnit.MISMATCHED, ctx=ctx)
        print("WARNING: error LU: {}".format(lu))
        dump(lu)
        miner.deactivate(*errors, ctx=ctx)


def dump(lu):
    header(lu)
    for r in lu:
        print(r.mode, r.dmrs())


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
