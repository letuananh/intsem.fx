#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing coolisf library
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import unittest
import logging
from collections import defaultdict as dd

from texttaglib.chirptext import FileHelper, header, TextReport
from texttaglib.chirptext import ttl
from lelesk import LeLeskWSD, LeskCache

from yawlib import YLConfig, WordnetSQL as WSQL

from coolisf import GrammarHub
from coolisf.gold_extract import export_to_visko, read_gold_mrs
from coolisf.util import read_ace_output
from coolisf.morph import Compound, Integral, Transformer, SimpleHeadedCompound as HCMP
from coolisf.model import Sentence, MRS, Reading

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

from test import TEST_DATA
wsql = WSQL(YLConfig.WNSQL30_PATH)
TEST_SENTENCES = 'data/tsdb/skeletons/fun.txt'
SAMPLE_MRS_FILE = os.path.join(TEST_DATA, 'sample_mrs.txt')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# TEST SCRIPTS
# ------------------------------------------------------------------------------

class TestData(object):

    def __init__(self):
        self.sent = self.get_sent()
        self.struct = self.get_struct()
        self.guard_dog = self.get_guard_dog()
        self.green_tea = self.get_green_tea()
        self.named = self.get_named()
        self.partial_named = self.get_partial_named()

    def get_sent(self):
        m = """[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:2> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg GEND: n PT: std ] ]
          [ pronoun_q<0:2> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _be_v_id<3:5> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<6:7> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _blue_a_1<8:12> LBL: h12 ARG0: e13 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x8 ]
          [ compound<13:23> LBL: h12 ARG0: e14 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x8 ARG2: x15 [ x IND: + PT: notpro ] ]
          [ udef_q<13:18> LBL: h16 ARG0: x15 RSTR: h17 BODY: h18 ]
          [ _guard_n_1<13:18> LBL: h19 ARG0: x15 ]
          [ _dog_n_1<19:23> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 h17 qeq h19 > ]"""
        sent = Sentence('It is a blue guard dog.')
        sent.add(m)
        return sent

    def get_struct(self):
        return self.get_guard_dog()

    def get_guard_dog(self):
        m = """[ TOP: h0 RELS: < [ compound<0:9> LBL: h1 ARG0: e4 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: x6 [ x IND: + NUM: sg PERS: 3 ] ARG2: x5 [ x IND: + PT: notpro ] ]
          [ udef_q<0:5> LBL: h2 ARG0: x5 RSTR: h7 ]
          [ _guard_n_1<0:5> LBL: h3 ARG0: x5 ]
          [ _dog_n_1<6:9> LBL: h1 ARG0: x6 ] >
  HCONS: < h0 qeq h1 h7 qeq h3 > ]"""
        sent = Sentence("guard dog")
        sent.add(m)
        return sent

    def get_green_tea(self):
        m = """[ TOP: h0
  INDEX: e2 [ e SF: prop-or-ques ]
  RELS: < [ unknown<0:9> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg ] ARG0: e2 ]
          [ udef_q<0:9> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ _green_a_2<0:5> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x4 ]
          [ _tea_n_1<6:9> LBL: h8 ARG0: x4 ] >
  HCONS: < h0 qeq h1 h6 qeq h8 > ]"""
        sent = Sentence("green tea")
        sent.add(m)
        return sent

    def get_named(self):
        m = """[ TOP: h0
  INDEX: e2 [ e SF: prop-or-ques ]
  RELS: < [ unknown<0:20> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ proper_q<0:20> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ compound<0:20> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x4 ARG2: x10 [ x PERS: 3 NUM: sg IND: + PT: notpro ] ]
          [ proper_q<0:15> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ]
          [ compound<0:15> LBL: h14 ARG0: e15 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x10 ARG2: x16 [ x PERS: 3 NUM: sg IND: + PT: notpro ] ]
          [ proper_q<0:7> LBL: h17 ARG0: x16 RSTR: h18 BODY: h19 ]
          [ named<0:7> LBL: h20 ARG0: x16 CARG: "Francis" ]
          [ named<8:15> LBL: h14 ARG0: x10 CARG: "Charles" ]
          [ named<16:20> LBL: h8 ARG0: x4 CARG: "Bond" ] >
  HCONS: < h0 qeq h1 h6 qeq h8 h12 qeq h14 h18 qeq h20 > ]"""
        sent = Sentence("Francis Charles Bond")
        sent.add(m)
        return sent

    def get_partial_named(self):
        m = """[ TOP: h0
  INDEX: e2 [ e SF: prop-or-ques ]
  RELS: < [ unknown<0:28> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg IND: + ] ARG0: e2 ]
          [ _the_q<0:3> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ]
          [ named_n<4:17> LBL: h8 ARG0: x4 CARG: "United_States" ]
          [ _of_p<18:20> LBL: h8 ARG0: e10 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x4 ARG2: x11 [ x PERS: 3 NUM: sg IND: + ] ]
          [ proper_q<21:28> LBL: h12 ARG0: x11 RSTR: h13 BODY: h14 ]
          [ named<21:28> LBL: h15 ARG0: x11 CARG: "America" ] >
  HCONS: < h0 qeq h1 h6 qeq h8 h13 qeq h15 > ]"""
        sent = Sentence("the United_States of America")
        sent.add(m)
        return sent

    def get_comp_rule(self):
        return Compound(self.get_struct()[0].edit(), "guard+dog")


class TestRuleGenerator(unittest.TestCase):

    optimus = Transformer()
    rdb = optimus.rdb

    def test_load_rule(self):
        with self.rdb.ctx() as ctx:
            words = self.rdb.find_lexunits(lemma='living thing', pos='n', ctx=ctx)
            self.assertGreater(len(words), 0)

    def test_gen_one_rule(self):
        rdb = self.rdb
        with rdb.ctx() as ctx:
            lu = rdb.find_lexunits(lemma='living thing', pos='n', ctx=ctx)[0]
            rdb.get_lexunit(lu)
            r = HCMP(lu[0].dmrs().layout, 'living+thing')
            self.assertIsInstance(r.construction.to_dmrs().to_mrs(), MRS)
            self.assertEqual(r.head().predstr, "_thing_n_of-about")

    def test_get_rule_from_db(self):
        rdb = self.rdb
        with rdb.ctx() as ctx:
            lu = rdb.find_lexunits(lemma='living thing', pos='n', ctx=ctx)[0]
            rdb.get_lexunit(lu)
            wid, pid = lu.ID, lu[0].ID
            ruleinfo = rdb.get_rule(wid, pid, ctx=ctx)
            rule = self.optimus.to_hcmp_rule(ruleinfo[0].dmrs().layout, "living+thing")
            self.assertIsInstance(rule, HCMP)
            self.assertIsNotNone(rule.dmrs())

    def test_link_rulepred(self):
        rdb = self.rdb
        with rdb.ctx() as ctx:
            ruleinfos = ctx.ruleinfo.select('ID not in (SELECT ruleid FROM rulepred)')
            for rinfo in ruleinfos:
                getLogger().debug(rinfo.ID, rinfo)
                rdb.generate_rulepred(rinfo, ctx=ctx)


class TestTransformer(unittest.TestCase):

    data = TestData()
    ghub = GrammarHub()
    ERG = ghub.ERG

    def test_merge_compound(self):
        header("Test merge compound")
        n = self.data.get_named()
        ne = n.edit(0)
        head = ne.top['ARG']
        comps = Integral.get_comps(head)
        self.assertEqual(len(comps), 1)
        Integral.merge_compound(comps[0], True)
        self.assertEqual(head.predstr, "named")
        self.assertEqual(head.carg, "Charles Bond")

    def test_raw_merge_operator(self):
        sent = self.data.get_struct()
        ded = sent[0].edit()
        comp = ded[10000]
        head = ded[10003]
        head.cfrom = comp.cfrom
        head.cto = comp.cto
        head.pred.lemma = "guard+dog"
        ded.delete(comp, 10001, 10002)
        ded.save()
        expected = """<dmrs cfrom="-1" cto="-1"><node cfrom="0" cto="9" nodeid="10003"><realpred lemma="guard+dog" pos="n" sense="1"/><sortinfo cvarsort="x" ind="+" num="sg" pers="3"/></node><link from="0" to="10003"><rargname/><post>H</post></link></dmrs>"""
        actual = sent[0].dmrs().xml_str()
        self.assertEqual(actual, expected)
        expected = '[ TOP: h0 RELS: < [ _guard+dog_n_1<0:9> LBL: h1 ARG0: x2 [ x NUM: sg PERS: 3 IND: + ] ] > HCONS: < h0 qeq h1 > ]'
        actual = sent[0].mrs().tostring(False)
        self.assertEqual(actual, expected)

    def test_named(self):
        # all are connected
        n = self.data.get_named()
        ne = n[0].edit()
        head = ne.top['ARG']
        self.assertEqual(head.carg, "Bond")
        self.assertTrue(Integral.is_named(head))
        # partial named
        n = self.data.get_partial_named()
        ne = n[0].edit()
        head = ne.top['ARG']
        self.assertEqual(head.carg, "United_States")
        self.assertFalse(Integral.is_named(head))

    def test_collapsing(self):
        n = self.data.get_named()
        ne = n.edit(0)
        head = ne.top['ARG']
        # Test collapsing
        Integral.collapse(head)
        self.assertEqual(len(ne.nodes), 3)
        self.assertEqual(ne.nodes[0].predstr, "unknown")
        self.assertEqual(ne.nodes[1].predstr, "proper_q")
        self.assertEqual(ne.nodes[2].predstr, "named")
        self.assertEqual(head.carg, "Francis Charles Bond")

    def test_transforming(self):
        """ Use a rule to transform a sub DMRS into a pred """
        se = self.data.get_sent().edit(0)
        comp = self.data.get_comp_rule()
        for m in comp.match(se):
            comp.transform(se, m)
        self.assertEqual(se.top['ARG2'].predstr, "_guard+dog_n_1")

    def test_green_tea(self):
        sent = Sentence("I like green tea.")
        sent.add("""[ TOP: h0 RELS: < [ pron<0:1> LBL: h1 ARG0: x6 [ x IND: + NUM: sg PERS: 1 PT: std ] ] [ pronoun_q<0:1> LBL: h2 ARG0: x6 RSTR: h10 ] [ _like_v_1<2:6> LBL: h3 ARG0: e7 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: pres ] ARG1: x6 ARG2: x9 [ x NUM: sg PERS: 3 ] ] [ udef_q<7:17> LBL: h4 ARG0: x9 RSTR: h11 ] [ _green_a_2<7:12> LBL: h5 ARG0: e8 [ e MOOD: indicative PERF: - PROG: bool SF: prop TENSE: untensed ] ARG1: x9 ] [ _tea_n_1<13:17> LBL: h5 ARG0: x9 ] > HCONS: < h0 qeq h3 h10 qeq h1 h11 qeq h5 > ]""")
        trans = Transformer(ruledb_path=None)
        trans.apply(sent)
        preds = set(sent[0].dmrs().preds())
        expected = {'udef_q_rel', '_like_v_1_rel', 'pron_rel', '_green+tea_n_1_rel', 'pronoun_q_rel'}
        self.assertEqual(preds, expected)
        # with a compound

    def test_all(self):
        parse = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ proper_q<0:20> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg IND: + ] RSTR: h5 BODY: h6 ]
          [ compound<0:20> LBL: h7 ARG0: e8 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x9 [ x PERS: 3 NUM: sg IND: + PT: notpro ] ]
          [ proper_q<0:7> LBL: h10 ARG0: x9 RSTR: h11 BODY: h12 ]
          [ named<0:7> LBL: h13 ARG0: x9 CARG: "Francis" ]
          [ compound<8:20> LBL: h7 ARG0: e15 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x3 ARG2: x16 [ x PERS: 3 NUM: sg IND: + PT: notpro ] ]
          [ proper_q<8:15> LBL: h17 ARG0: x16 RSTR: h18 BODY: h19 ]
          [ named<8:15> LBL: h20 ARG0: x16 CARG: "Charles" ]
          [ named<16:20> LBL: h7 ARG0: x3 CARG: "Bond" ]
          [ _love_v_1<21:26> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x23 [ x PERS: 3 NUM: pl IND: + ] ]
          [ udef_q<27:38> LBL: h24 ARG0: x23 RSTR: h25 BODY: h26 ]
          [ compound<27:38> LBL: h27 ARG0: e28 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x23 ARG2: x29 [ x IND: + PT: notpro ] ]
          [ udef_q<27:32> LBL: h30 ARG0: x29 RSTR: h31 BODY: h32 ]
          [ _guard_n_1<27:32> LBL: h33 ARG0: x29 ]
          [ _dog_n_1<33:38> LBL: h27 ARG0: x23 ] >
  HCONS: < h0 qeq h1 h5 qeq h7 h11 qeq h13 h18 qeq h20 h25 qeq h27 h31 qeq h33 > ]""")
        optimus = Transformer(ruledb_path=None)
        optimus.apply(parse)
        preds = set(parse.dmrs().preds())
        self.assertEqual(preds, {'proper_q_rel', 'named_rel', '_love_v_1_rel', 'udef_q_rel', '_guard+dog_n_1_rel'})

    def gen_adj(self, sub):
        adj_list = dd(list)
        for n in sub.nodes:
            # ignore RSTR
            if n.is_unk() or (not n.in_links and len(n.out_links) == 1 and n.out_links[0].is_rstr()):
                continue
            adj_list[n.cfrom].append(n)
            adj_list[n.cto + 1].append(n)
        return {frozenset(n.predstr for n in v) for k, v in adj_list.items() if len(v) > 1}

    def test_adjacent(self):
        """ Generate a list of predicates that are adjacent """
        p = self.ERG.parse('green tea').edit(0)
        adj_list = p.adjacent_nodes()
        expected = {frozenset({'_green_a_2', '_tea_n_1'})}
        self.assertEqual(adj_list, expected)

    def test_big_bad_wolf(self):
        sent = self.ERG.parse('He is a big bad wolf.')
        p = sent.edit(0)
        p2 = sent.edit(0)
        optimus = Transformer(ruledb_path=None)  # only manual rule
        optimus.apply(p)
        nodes = {n.predstr for n in p.nodes}
        expected = {'pron', 'pronoun_q', '_be_v_id', '_a_q', '_big+bad+wolf_n_1'}
        getLogger().debug("Output: {}".format(expected))
        self.assertEqual(nodes, expected)
        getLogger().debug("Optimus 2")
        optimus2 = Transformer()  # with ruleDB
        optimus2.apply(p2)
        getLogger().debug("p2 actual: {}".format(p2.nodes))
        p2_actual = {n.predstr for n in p2.nodes}
        self.assertEqual(p2_actual, expected)

    def test_load_rule_db(self):
        sent = self.ERG.parse('He is a bell ringer.')
        p = sent.edit(1)
        ringer = p.top['ARG2']
        self.assertEqual(ringer.predstr, "_ringer_n_1")
        # Load a rule from optimus
        optimus = Transformer()
        rules = optimus.find_rules(p.nodes)
        self.assertTrue(rules)
        lemmas = [r.lemma for r in rules]
        self.assertIn('bell+ringer', lemmas)
        rule = None
        for r in rules:
            if r.sign == '_ringer_n_1' and r.lemma == 'bell+ringer':
                rule = r
                break
        self.assertEqual(rule.dmrs().preds(), ['compound_rel', 'udef_q_rel', '_bell_n_1_rel', '_ringer_n_1_rel'])
        # compare graph manually
        sub = p.subgraph(ringer, constraints=rule.construction)
        self.assertEqual(sub.top.to_graph(), rule.graph)
        # apply rule & save manually
        rule.apply(p).save()
        expected = ['pron_rel', 'pronoun_q_rel', '_be_v_id_rel', '_a_q_rel', '_bell+ringer_n_1_rel']
        self.assertEqual(p.source.preds(), expected)

    def test_smart_rule_search(self):
        sent = self.ERG.parse('His name is John.')
        p = sent.edit(0)
        john = p.head()['ARG2']
        getLogger().debug(john)
        # Load a rule from optimus
        optimus = Transformer()
        rules = optimus.find_rules((john,))
        getLogger().debug(len(rules))

    def test_finding_rules(self):
        optimus = Transformer()
        rules = optimus.rdb.find_ruleinfo_by_head('_contact_n_1')
        signs = [optimus.rdb.get_rule(rule.lid, rule.rid).lemma for rule in rules]
        self.assertIn('eye contact', signs)
        rules = optimus.rdb.find_ruleinfo_by_head('_chest_n_1')
        signs = [optimus.rdb.get_rule(rule.lid, rule.rid).lemma for rule in rules]
        self.assertIn('tea chest', signs)

    def test_rule_matching(self):
        optimus = Transformer()
        sent = self.ERG.parse('I made it.')
        d = sent[0].dmrs()
        # find applicable rules
        applicable_rules = optimus.find_rules(d.layout.nodes)
        mafs = []
        for r in applicable_rules:
            if r.lemma == 'make+a+face':
                mafs.append(r)
        for maf in mafs:
            subs = maf.match(d.layout)
            if subs:
                getLogger().debug("-" * 20)
                getLogger().debug("{} is matched with {}".format(maf.construction.to_dmrs().to_mrs(), subs[0].to_dmrs()))
                getLogger().debug("sub: {} {}".format(subs[0].top.to_graph(), subs[0].nodes))
                getLogger().debug("maf: {} {}".format(maf.graph, maf.construction.nodes))
        optimus.apply(d)

    def test_subgraph(self):
        g1 = """[ TOP: h0
  RELS: < [ unknown<0:12> LBL: h1 ARG: x5 [ x NUM: pl PERS: 3 IND: + ] ARG0: e4 [ e SF: prop-or-ques ] ]
          [ udef_q<0:4> LBL: h2 ARG0: x5 RSTR: h6 ]
          [ _five+finger_n_1<0:12> LBL: h3 ARG0: x5 ] >
  HCONS: < h0 qeq h1 h6 qeq h3 > ]"""

    def test_optimus_rule_db(self):
        optimus = Transformer()
        sent = self.ERG.parse('We made eye contact.')
        optimus.apply(sent)
        expected = ['pron_rel', 'pronoun_q_rel', '_make_v_1_rel', 'udef_q_rel', '_eye+contact_n_1_rel']
        actual = [str(p) for p in sent[0].dmrs().preds()]
        getLogger().debug("Expected: {}".format(expected))
        getLogger().debug("Actual: {}".format(actual))
        self.assertEqual(actual, expected)

    def test_transform_darklantern(self):
        r = Reading("""[ TOP: h0
  RELS: < [ person<0:7> LBL: h1 ARG0: x8 [ x NUM: sg PERS: 3 ] ]
          [ _some_q<0:7> LBL: h2 ARG0: x8 RSTR: h15 ]
          [ _in_p_loc<8:10> LBL: h1 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x8 ARG2: x11 [ x NUM: sg PERS: 3 IND: + ] ]
          [ _the_q<11:14> LBL: h3 ARG0: x11 RSTR: h16 ]
          [ _next_a_1<15:19> LBL: h4 ARG0: e10 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x11 ]
          [ _room_n_unit<20:24> LBL: h4 ARG0: x11 ]
          [ _light_v_cause<29:32> LBL: h5 ARG0: e12 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: + ] ARG1: x8 ARG2: x14 [ x NUM: sg PERS: 3 IND: + ] ]
          [ _a_q<33:34> LBL: h6 ARG0: x14 RSTR: h17 ]
          [ _dark_a_1<35:40> LBL: h7 ARG0: e13 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x14 ]
          [ _lantern_n_1<40:48> LBL: h7 ARG0: x14 ] >
  HCONS: < h0 qeq h5 h15 qeq h1 h16 qeq h4 h17 qeq h7 > ]""")
        getLogger().debug("Adjacent: {}".format(r.dmrs().layout.adjacent_nodes()))
        optimus = Transformer()
        # test matching preds
        rules = optimus.find_rules(r.dmrs().layout.nodes)
        getLogger().debug(r.dmrs())
        for rule in rules:
            getLogger().debug("MATCHING {}: {} -> {}".format(rule.lemma, rule.construction.to_dmrs(), rule.match(r.dmrs().layout)))
        optimus.apply(r)
        getLogger().debug("Final: {}".format(r.dmrs().layout.nodes))

    def test_long_sentence(self):
        r = Reading("""[ TOP: h0
  RELS: < [ part_of<3:6> LBL: h1 ARG0: x25 [ x NUM: pl PERS: 3 ] ARG1: x27 [ x NUM: pl PERS: 3 IND: + ] ]
          [ _all_q<3:6> LBL: h2 ARG0: x25 RSTR: h49 ]
          [ _these_q_dem<7:12> LBL: h3 ARG0: x27 RSTR: h50 ]
          [ _vary_v_cause<13:19> LBL: h4 ARG0: e26 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG2: x27 ]
          [ _case_n_of<20:26> LBL: h4 ARG0: x27 ]
          [ _however_a_1<27:35> LBL: h5 ARG0: i28 ARG1: h51 ]
          [ pron<36:37> LBL: h6 ARG0: x29 [ x NUM: sg PERS: 1 IND: + PT: std ] ]
          [ pronoun_q<36:37> LBL: h7 ARG0: x29 RSTR: h52 ]
          [ neg<38:44> LBL: h8 ARG0: e30 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: h53 ]
          [ _can_v_modal<38:44> LBL: h9 ARG0: e31 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: h54 ]
          [ _recall_v_1<45:51> LBL: h10 ARG0: e32 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x29 ARG2: x33 [ x NUM: pl PERS: 3 ] ]
          [ _any_q<52:55> LBL: h11 ARG0: x33 RSTR: h55 ]
          [ part_of<52:55> LBL: h12 ARG0: x33 ARG1: x25 ]
          [ _present_v_to<62:71> LBL: h12 ARG0: e34 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ] ARG1: x33 ARG2: x37 [ x NUM: pl PERS: 3 IND: + ] ]
          [ udef_q<72:191> LBL: h13 ARG0: x37 RSTR: h56 ]
          [ _more_x_comp<72:76> LBL: h14 ARG0: e35 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e36 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG2: x38 [ x NUM: sg PERS: 3 GEND: n ] ]
          [ _singular_a_1<77:85> LBL: h14 ARG0: e36 ARG1: x37 ]
          [ _feature_n_1<86:94> LBL: h14 ARG0: x37 ]
          [ generic_entity<100:104> LBL: h15 ARG0: x38 ]
          [ _that_q_dem<100:104> LBL: h16 ARG0: x38 RSTR: h57 ]
          [ _associate_v_with<115:125> LBL: h15 ARG0: e39 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ] ARG2: x38 ARG3: x44 [ x NUM: sg PERS: 3 IND: + ] ]
          [ _the_q<131:134> LBL: h17 ARG0: x44 RSTR: h58 ]
          [ _well_x_deg<135:140> LBL: h18 ARG0: e40 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: e41 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ]
          [ _know_v_1<140:145> LBL: h18 ARG0: e41 ARG2: x44 ]
          [ compound<146:159> LBL: h18 ARG0: e42 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x44 ARG2: x43 [ x NUM: sg PERS: 3 IND: + PT: notpro ] ]
          [ proper_q<146:152> LBL: h19 ARG0: x43 RSTR: h59 ]
          [ named<146:152> LBL: h20 ARG0: x43 CARG: "Surrey" ]
          [ _family_n_of<153:159> LBL: h18 ARG0: x44 ]
          [ _of_p<160:162> LBL: h18 ARG0: e45 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x44 ARG2: x46 [ x NUM: pl PERS: 3 IND: + ] ]
          [ _the_q<163:166> LBL: h21 ARG0: x46 RSTR: h60 ]
          [ named<167:175> LBL: h22 ARG0: x46 CARG: "Roylotts" ]
          [ _of_p<176:178> LBL: h22 ARG0: e47 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x46 ARG2: x48 [ x NUM: sg PERS: 3 IND: + ] ]
          [ proper_q<179:191> LBL: h23 ARG0: x48 RSTR: h61 ]
          [ named<179:191> LBL: h24 ARG0: x48 CARG: "Stoke Moran" ] >
  HCONS: < h0 qeq h5 h49 qeq h1 h50 qeq h4 h51 qeq h8 h52 qeq h6 h53 qeq h9 h54 qeq h10 h55 qeq h12 h56 qeq h14 h57 qeq h15 h58 qeq h18 h59 qeq h20 h60 qeq h22 h61 qeq h24 > ]
""")
        optimus = Transformer()
        rules = optimus.find_rules(r.dmrs().layout.nodes, limit=100)
        with TextReport.null() as outfile:
            for rule in rules:
                outfile.print(rule.lemma, rule.head(), rule.construction.to_dmrs())
        optimus.apply(r)
        getLogger().debug(r.edit().nodes)

    def test_named_rel_ruledb(self):
        optimus = Transformer()
        sent = self.ERG.parse('It is called Nemean Games.')
        optimus.apply(sent)
        print(sent[0].dmrs().preds())


class TestERGISF(unittest.TestCase):

    ghub = GrammarHub()
    ERG = ghub.ERG
    EI = ghub.ERG_ISF

    def test_erg_isf(self):
        p = self.EI.parse("He is a big bad wolf.").edit(0)
        preds = p.source.preds()
        expected = ['pron_rel', 'pronoun_q_rel', '_be_v_id_rel', '_a_q_rel', '_big+bad+wolf_n_1_rel']
        self.assertEqual(preds, expected)

    def test_tea_chest(self):
        sent = self.EI.parse("I have a tea chest.")
        self.assertEqual(sent[0].edit().preds(), ['pron', 'pronoun_q', '_have_v_1', '_a_q', '_tea+chest_n_1'])

    def test_named_rel(self):
        sent = self.EI.parse("My name is Sherlock Holmes.")
        sent.tag_xml(ttl.Tag.LELESK)
        getLogger().debug(sent[0].dmrs().xml_str(pretty_print=True))


class TestMain(unittest.TestCase):

    ghub = GrammarHub()
    ERG = ghub.ERG

    def test_models(self):
        raw_text = 'It rains.'
        raw_mrs = """[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]"""
        sent = Sentence(raw_text, 1)
        sent.add(raw_mrs)
        self.assertEqual(sent.text, raw_text)
        self.assertEqual(len(sent), 1)
        self.assertIsNotNone(sent[0].mrs())
        self.assertIsNotNone(sent[0].dmrs())
        self.assertIsNotNone(sent[0].dmrs().to_mrs())
        self.assertIsNotNone(sent[0].mrs().to_dmrs())

    def test_ace_output_to_xml(self):
        sentences = read_ace_output(SAMPLE_MRS_FILE)
        self.assertIsNotNone(sentences)

        sent = sentences[3]
        getLogger().debug(sent)
        self.assertGreaterEqual(len(sent), 3)
        # sentence to XML
        xml = sent.to_xml_node()
        self.assertIsNotNone(xml)
        # ensure DMRS nodes count
        dmrs_nodes = xml.findall('./reading/dmrs')
        self.assertGreaterEqual(len(dmrs_nodes), 3)

    def test_txt_to_dmrs(self):
        print("Test parsing raw text sentences")
        sent = self.ERG.parse("It rains.")
        sent.tag_xml(method=ttl.Tag.MFS)
        sent_xml = sent.to_xml_node()
        sent_re = Sentence.from_xml_node(sent_xml)
        getLogger().debug(sent_re.to_xml_str())
        tags = sent_re[0].dmrs().tags
        self.assertTrue(tags)
        self.assertEqual(tags[10000][0].synset.lemma, 'rain')
        self.assertEqual(tags[10000][0].method, ttl.Tag.MFS)

    def test_sensetag_in_json(self):
        text = "Some dogs chase a cat."
        a_sent = self.ERG.parse(text)
        p = a_sent[0]
        # check json
        self.assertEqual(type(p.dmrs().json()), dict)
        self.assertEqual(type(p.dmrs().json_str()), str)
        # check sense tagging
        tags = p.dmrs().tag(method=ttl.Tag.MFS)
        j = p.dmrs().json()
        getLogger().debug("{} -> {}".format(text, j))
        nodes = j['nodes']
        self.assertGreaterEqual(len(nodes), 5)
        self.assertGreaterEqual(len(tags), 4)
        for node in nodes:
            if node['predicate'] in ('_some_q', '_dog_n_1', '_cat_n_1'):
                self.assertEqual(len(node['senses']), 1)
            if node['predicate'] == '_chase_v_1':
                self.assertEqual(node['pos'], 'v')
            if node['predicate'].startswith('_'):
                self.assertEqual(node['type'], 'realpred')
            else:
                self.assertEqual(node['type'], 'gpred')

    def test_mrs_formats(self):
        text = "Some dogs chase some cats."
        a_sent = self.ERG.parse(text)
        p = a_sent[0]
        # Create sentence object from raw data
        sent = Sentence(a_sent.text)
        sent.add(p.mrs().tostring())
        self.assertIsNotNone(sent)
        p2 = sent[0]
        self.assertEqual(len(sent), 1)
        self.assertEqual(str(p2.mrs().tostring())[:20], '[ TOP: h0\n  INDEX: e')
        # now make DMRS XML ...
        xml_str = p2.dmrs().xml_str()
        self.assertTrue(xml_str.startswith('<dmrs cfrom="'))
        # add new DMRS from XML
        sent.add(dmrs_xml=xml_str)
        self.assertEqual(len(sent), 2)  # now we should have 2 MRSes
        m2 = sent[1]
        # and they should look exactly the same
        xml_str2 = m2.dmrs().xml_str()
        self.assertEqual(xml_str, xml_str2)
        pass

    def test_lelesk_integration(self):
        text = "A big bird is flying on the sky."
        a_sent = self.ERG.parse(text)
        context = [p.pred.lemma for p in a_sent[0].dmrs().obj().eps()]
        preds = a_sent[0].dmrs().obj().eps()
        wsd = LeLeskWSD(dbcache=LeskCache())
        for w, p in zip(context, preds):
            scores = wsd.lelesk_wsd(w, '', lemmatizing=False, context=context)
            if scores:
                getLogger().debug("Word: {w} (p={p}|{nid}) => {ss} | Score: {sc} | Def: {d}".format(w=w, p=str(p.pred), nid=p.nodeid, ss=scores[0].candidate.synset, sc=scores[0].score, d=scores[0].candidate.synset.glosses[0].text()))
            else:
                getLogger().debug("Word: {w} => N/A".format(w=w))

    def test_sensetag_using_lelesk(self):
        text = "A big bird is flying on the sky."
        logging.info("Tagging ``{s}'' using lelesk".format(s=text))
        a_sent = self.ERG.parse(text)
        d = a_sent[0].dmrs()
        d.tag(method='lelesk')
        self.assertTrue(d.tags)
        js = d.json_str()
        getLogger().debug("Tagged JSON (using LeLesk): {}".format(js))

    def test_erg_isf_lelesk(self):
        s = self.ghub.ERG_ISF.parse("Ali Baba didn't drink green tea.")
        d = s[0].dmrs()
        d.tag(method='lelesk')
        getLogger().debug(d.layout.nodes)
        getLogger().debug("tags: {}".format(d.tags))
        self.assertGreaterEqual(len(d.tags.keys()), 3)

    def test_transforming_special_preds(self):
        s = self.ghub.ERG_ISF.parse("My name is Sherlock Holmes.")
        s.tag_xml(method=ttl.Tag.LELESK, update_back=False)
        s.tag_xml(method=ttl.Tag.MFS, update_back=False)
        s.tag_xml(method=ttl.Tag.MFS, update_back=False)
        dmrs_xml = s[0].dmrs().xml()
        for node in dmrs_xml.findall('node'):
            senses = node.findall('sense')
            if senses:
                self.assertEqual(len(senses), 2)
        # getLogger().debug(s[0].dmrs().xml_str(pretty_print=True))
        # for k, v in s[0].dmrs().tags.items():
        #     getLogger().debug("{}: {}".format(k, v))
        for reading in s:
            for nodeid, tags in reading.dmrs().tags.items():
                self.assertEqual(len(tags), 2)
                self.assertEqual({t.method for t in tags}, {ttl.Tag.MFS, ttl.Tag.LELESK})

    def test_parse_no(self):
        text = "I saw a girl with a big telescope which is nice."
        a_sent = self.ERG.parse(text)
        self.assertEqual(len(a_sent), 5)  # default is 5
        # increase parse count to 7
        a_sent = self.ERG.parse(text, parse_count=7)
        self.assertEqual(len(a_sent), 7)
        # increase parse count to 10
        a_sent = self.ERG.parse(text, parse_count=10)
        self.assertEqual(len(a_sent), 10)

    def test_generation(self):
        text = 'I did it.'
        sent = self.ERG.parse(text)
        g_sents = self.ERG.generate(sent[0])
        texts = [g.text for g in g_sents]
        self.assertIn('I did it.', texts)
        self.assertIn('It was done by me.', texts)

    def test_generation_jp(self):
        text = '雨が降る。'
        JACYDK = self.ghub.JACYDK
        sent = JACYDK.parse(text)
        g_sents = JACYDK.generate(sent[0])
        texts = [g.text for g in g_sents]
        self.assertIn('雨 が 降る', texts)

    def test_mrs_xml(self):
        mrs = """[ TOP: h0
  RELS: < [ def_explicit_q_rel<0:3> LBL: h1 ARG0: x12 [ x NUM: sg IND: + PERS: 3 ] RSTR: h17 ]
          [ poss_rel<0:3> LBL: h2 ARG0: e10 [ e MOOD: indicative PERF: - SF: prop PROG: - TENSE: untensed ] ARG1: x12 ARG2: x11 [ x NUM: sg PT: std PERS: 1 ] ]
          [ pronoun_q_rel<0:3> LBL: h3 ARG0: x11 RSTR: h18 ]
          [ pron_rel<0:3> LBL: h4 ARG0: x11 ]
          [ _name_n_of_rel<4:8> LBL: h2 ARG0: x12 ]
          [ _be_v_id_rel<9:11> LBL: h5 ARG0: e13 [ e MOOD: indicative PERF: - SF: prop PROG: - TENSE: pres ] ARG1: x12 ARG2: x16 [ x NUM: sg IND: + PERS: 3 ] ]
          [ proper_q_rel<12:28> LBL: h6 ARG0: x16 RSTR: h19 ]
          [ compound_rel<12:28> LBL: h7 ARG0: e14 [ e MOOD: indicative PERF: - SF: prop PROG: - TENSE: untensed ] ARG1: x16 ARG2: x15 [ x NUM: sg PT: notpro IND: + PERS: 3 ] ]
          [ proper_q_rel<12:20> LBL: h8 ARG0: x15 RSTR: h20 ]
          [ named_rel<12:20> LBL: h9 ARG0: x15 CARG: "Sherlock" ]
          [ named_rel<21:28> LBL: h7 ARG0: x16 CARG: "Holmes" ] >
  HCONS: < h0 qeq h5 h17 qeq h2 h18 qeq h4 h19 qeq h7 h20 qeq h9 > ]
"""
        sent = Sentence()
        sent.add(mrs)
        sent.add(dmrs_xml=sent[0].dmrs().xml_str())
        self.assertEqual(sent[0].dmrs().json(), sent[1].dmrs().json())

    def text_isf_visko(self):
        sents = read_gold_mrs()
        s10044 = sents[44]
        # test export to visko (XML)
        FileHelper.create_dir(TEST_DATA)
        export_to_visko([s10044], TEST_DATA)

    def test_preserve_xml_tag_in_json(self):
        sent = self.ERG.parse('He likes green tea.')
        sent.tag(ttl.Tag.MFS)
        d = sent[0].dmrs()
        self.assertIsNotNone(d.json_str())
        tea_node = None
        for n in d.layout.nodes:
            if n.predstr == '_tea_n_1':
                tea_node = n
        getLogger().debug("Nodes: {}".format(d.layout.nodes))
        getLogger().debug("Tags: {}".format(d.tags))
        self.assertIsNotNone(tea_node)
        self.assertEqual(len(d.tags), 3)
        self.assertEqual(len(d.tags[tea_node.nodeid]), 1)
        ss, method = d.tags[tea_node.nodeid][0]
        getLogger().debug("JSON str: {}".format(d.json_str()))

    def test_preserve_shallow(self):
        txt = "雨が降る。"
        sent = self.ghub.parse_json(txt, "JACYDK")
        # load cached
        cached = self.ghub.cache.load(txt, "JACYDK", None, None)
        self.assertEqual(cached["shallow"], sent["shallow"])


########################################################################

if __name__ == "__main__":
    unittest.main()
