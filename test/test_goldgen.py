#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for gold data generator
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import unittest
import logging
from collections import defaultdict as dd
from lxml import etree
from delphin.mrs.components import Pred

from texttaglib.chirptext import header, Counter, TextReport
from texttaglib.chirptext import texttaglib as ttl
from coolisf import tag_gold, Lexsem
from coolisf.lexsem import import_shallow
from coolisf.gold_extract import build_root_node
from coolisf.gold_extract import filter_wrong_senses, read_gold_sents
from coolisf.gold_extract import read_gold_mrs, read_tsdb, match_sents, read_tsdb_ttl
from coolisf import GrammarHub


# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

TEST_GOLD_DIR = 'data'
GOLD_TSDB = 'data/gold'
GOLD_FIXED = 'data/gold_fixed'
ghub = GrammarHub()
ERG = ghub.ERG


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# TEST SCRIPTS
# ------------------------------------------------------------------------------

class TestShallowDMRSMapping(unittest.TestCase):

    doc_dir = 'data'
    doc_name = 'gold'

    def test_reading_gold(self):
        ttl_doc = ttl.Document.read_ttl(GOLD_FIXED)
        self.assertTrue(ttl_doc)
        self.assertEqual(len(ttl_doc), 599)

    def test_reading_tsdb(self):
        tsdb_doc = read_tsdb(GOLD_TSDB)
        self.assertTrue(tsdb_doc)
        self.assertEqual(len(tsdb_doc), 599)

    def test_mapping(self):
        ttl_doc = ttl.Document.read_ttl(GOLD_FIXED)
        tsdb_doc = read_tsdb(GOLD_TSDB)
        isf_doc = match_sents(tsdb_doc, ttl_doc)
        self.assertTrue(isf_doc)
        for s in isf_doc:
            import_shallow(s)

    def test_read_isf(self):
        doc = read_tsdb_ttl('data/gold')
        sent = doc[0]
        print(doc.name)
        self.assertTrue(sent.shallow.concepts)
        self.assertTrue(sent[0].dmrs().tags)
        for s in doc[:5]:
            self.assertEqual(s.ident, s.shallow.ID)


class TestGoldAccuracy(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__gold = None

    @property
    def gold(self):
        if not self.__gold:
            self.__gold = read_tsdb_ttl(GOLD_TSDB, ttl_path=GOLD_FIXED)
        return self.__gold

    def test_accuracy(self):
        c = Counter()
        sent = self.gold[0]  # gold MRS
        sent.tag(method=ttl.Tag.LELESK)  # perfrom WSD using LeLESK
        d = sent[0].dmrs()
        getLogger().debug(d.tags)
        for k, v in d.tags.items():
            print("v=", v)
            g, l = v
            if g.synset.ID == l.synset.ID:
                c.count("same")
            else:
                getLogger().debug("{} {} {}".format(d.layout[k].pred, g.synset.ID, l.synset.ID))
                c.count("diff")
        c.summarise()


class TestGoldData(unittest.TestCase):

    _singleton_gold = None

    def gold(self):
        if self._singleton_gold is None:
            self._singleton_gold = read_gold_sents()
        return self._singleton_gold

    def build_root_node(self):
        node = build_root_node()
        self.assertTrue(etree.tostring(node, pretty_print=True).decode('utf-8'))

    def test_read_gold_mrses(self):
        sents = self.gold()
        self.assertEqual(len(sents), 599)
        self.assertEqual(len(sents[0]), 1)
        self.assertTrue(sents[0].readings[0].mrs())

    def test_read_gold_tags(self):
        doc = ttl.Document('gold', TEST_GOLD_DIR).read()
        self.assertEqual(len(doc), 599)
        self.assertTrue(doc[0].to_json())

    def test_generate_latex(self):
        sents = self.gold()
        s = sents[0]
        self.assertTrue(s.to_latex())

    def test_sent2latex(self):
        txt = 'Everyone is a soul.'
        ghub = GrammarHub()
        s = ghub.parse(txt, "ERG")
        out = s.to_latex()
        for i in range(1, 3):
            self.assertIn('%%% {}'.format(i), out)

    def test_ep_types(self):
        sid = 10598
        sents = self.gold()
        smap = {int(s.ident): s for s in sents}
        dobj = smap[sid][0].dmrs().obj()
        eps = dobj.eps()
        for ep in eps:
            if ep.nodeid == 10015:
                self.assertEqual(ep.pred.type, Pred.GRAMMARPRED)
        # access by nodeid
        self.assertEqual(dobj.ep(10015).pred, 'named_rel')

    def test_lelesk_tagging(self):
        sents = self.gold()
        sents[0].tag(method=ttl.Tag.MFS)
        self.assertTrue(sents[0].to_xml_str())

    def test_flag_not_matched_concept(self):
        """ Lexsem should flag the not matched concepts """
        sid = '10322'
        sents = self.gold()
        smap = {str(s.ident): s for s in sents}
        sent = smap[sid]
        dmrs = sent[0].dmrs()
        doc = ttl.Document('gold', TEST_GOLD_DIR).read()
        tagged = doc.get(sid)
        m, n, ignored = tag_gold(dmrs, tagged, sent.text)
        self.assertGreater(len(m), 0)

    def test_read_tags(self):
        doc = ttl.Document('gold', TEST_GOLD_DIR).read()
        for tagged in doc:
            for w, concepts in tagged.tcmap().items():
                actual = {"{}-{}".format(c.clemma, c.tag) for c in concepts}
                self.assertEqual(len(actual), len(concepts), "WARNING: duplicate concept (w={} | c={})".format(w, concepts))

    def test_tag_one_sent(self):
        getLogger().debug("Test tagging one sentence")
        sid = '10081'
        sents = self.gold()
        smap = {str(s.ident): s for s in sents}
        sent = smap[sid]
        doc = ttl.Document('gold', TEST_GOLD_DIR).read()
        sent.shallow = doc.get(sid)
        if sent.text != sent.shallow.text:
            getLogger().debug("WARNING: Inconsistent")
            getLogger().debug(sent.text)
            getLogger().debug(sent.shallow.text)
        dmrs = sent[0].dmrs()
        # print(sent.to_xml_str())
        m, n, ignored = tag_gold(dmrs, sent.shallow, sent.text)
        header("#{}: {}".format(sid, sent.text), 'h0')
        getLogger().debug(sent[0].dmrs())
        header('Available concepts')
        for c in sent.shallow.concepts:
            getLogger().debug("{} {}".format(c, c.tokens))
        header('Matched')
        for con, nid, pred in m:
            getLogger().debug("{}::{} => #{}::{}".format(con.tag, con.clemma, nid, pred))
        header("Not matched")
        if n:
            for c in n:
                getLogger().debug(c)
        else:
            getLogger().debug("All was matched.")
        sent.tag(method=ttl.Tag.MFS)
        xml_str = sent.tag_xml().to_xml_str()
        self.assertTrue(xml_str)
        self.assertIn("<sensegold", xml_str)
        self.assertIn("<sense", xml_str)
        getLogger().debug(sent.to_xml_str())

    def test_gen_gold(self):
        sents = read_gold_mrs()
        doc = ttl.Document('gold', TEST_GOLD_DIR).read()
        for s in sents[:5]:
            if len(s) > 0:
                # tag it
                tagged = doc.get(str(s.ident))
                tag_gold(s[0].dmrs(), tagged, s.text)

    def test_generate_from_gold(self):
        header("Test generating from gold (THIS CAN BE VERY SLOW)")
        sents = self.gold()
        c = Counter()
        for sent in sents[:2]:
            if len(sent) > 0:
                try:
                    gsents = ERG.generate(sent[0])
                    c.count("OK" if gsents else "ERR")
                except:
                    c.count("BROKEN")
            else:
                c.count("SKIP")
        c.summarise()

    def test_tagging_all(self):
        getLogger().debug("Tagging everything ...")
        sents = self.gold()
        smap = {str(s.ident): s for s in sents}
        # reag tags
        doc = ttl.Document('gold', TEST_GOLD_DIR).read()
        filter_wrong_senses(doc)
        count_good_bad = Counter()
        perfects = []
        to_be_checked = dd(list)
        tbc_concepts = dd(list)
        concept_count = Counter()
        fix_texts = []
        instances = Counter()
        tag_map = dd(set)
        report = TextReport('data/gold_report.txt')
        matched_report = TextReport('data/gold_matched.txt')
        not_matched_report = TextReport('data/gold_notmatched.txt')
        for s in sents[:5]:
            sid = str(s.ident)
            if not doc.has_id(sid):
                raise Exception("Cannot find sentence {}".format(sid))
            elif len(s) == 0:
                logging.warning("Empty sentence: {}".format(s))
            else:
                tagged = doc.get(sid)
                if s.text != tagged.text:
                    fix_texts.append((s.ident, s.text, tagged.text))
                # try to tag ...
                dmrs = s[0].dmrs()
                matched, not_matched, ignored = tag_gold(dmrs, tagged, s.text, mode=Lexsem.ROBUST)
                if not not_matched:
                    count_good_bad.count("Perfect")
                    perfects.append((s, matched))
                else:
                    for nm in not_matched:
                        tag_map[nm.tag].add(nm.clemma)
                        tbc_concepts[nm.tag].append(s.ident)
                        concept_count.count(nm.tag)
                        instances.count('instances')
                    to_be_checked[s.ident].append(nm)
                    count_good_bad.count("To be checked")
        # report matched
        for sent, m in perfects:
            tagged = doc.get(str(sent.ident))
            matched_report.header("#{}: {}".format(sent.ident, sent.text), "h0")
            matched_report.writeline(sent[0].dmrs())
            matched_report.header("Concepts")
            for c, nid, pred in m:
                matched_report.writeline("{} ===> {}:{}".format(c, nid, pred))
            matched_report.writeline()
            matched_report.writeline()
        # report not matched
        not_matched_report.header("By senses", "h0")
        for k, v in concept_count.most_common():
            sids = ' '.join(["#{}".format(x) for x in tbc_concepts[k]])
            not_matched_report.print("{}: {} | {} => {}".format(k, v, sids, tag_map[k]))
        not_matched_report.header("By sentences", "h0")
        for sid, nm in to_be_checked.items():
            not_matched_report.print("#{}: {}  | {}".format(sid, nm, smap[str(sid)].text))
        # full details
        for sid, nm in to_be_checked.items():
            sent = smap[str(sid)]
            tagged = doc.get(str(sid))
            not_matched_report.header("#{}: {}".format(sid, sent.text))
            not_matched_report.writeline(sent[0].dmrs())
            for n in nm:
                not_matched_report.writeline(n)

        # for i, t1, t2 in fix_texts:
        #     getLogger().debug(i)
        #     getLogger().debug(t1)
        #     getLogger().debug(t2)
        count_good_bad.summarise(report=report)
        instances.summarise(report=report)


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
