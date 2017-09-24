#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for gold data generator
Latest version can be found at https://github.com/letuananh/coolisf

References:
    Python unittest documentation:
        https://docs.python.org/3/library/unittest.html
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 0257 - Python Docstring Conventions:
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

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, coolisf"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import unittest
import logging
from collections import defaultdict as dd
from delphin.mrs.components import Pred

from chirptext import header, Counter, TextReport
from chirptext.texttaglib import TaggedDoc, TagInfo
from coolisf import tag_gold, Lexsem
from coolisf.gold_extract import filter_wrong_senses
from coolisf.gold_extract import extract_tsdb_gold
from coolisf.gold_extract import read_gold_mrs
from coolisf import GrammarHub


# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_GOLD_DIR = 'data'
ghub = GrammarHub()
ERG = ghub.ERG


# ------------------------------------------------------------------------------
# TEST SCRIPTS
# ------------------------------------------------------------------------------

class TestGoldData(unittest.TestCase):

    def test_read_tsdb(self):
        gold = extract_tsdb_gold()
        self.assertTrue(gold)

    def test_read_gold_mrses(self):
        sents = read_gold_mrs()
        self.assertEqual(len(sents), 599)
        self.assertEqual(len(sents[0]), 1)
        self.assertTrue(sents[0].readings[0].mrs())

    def test_read_gold_tags(self):
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        self.assertEqual(len(doc), 599)

    def test_goldtags_json(self):
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        self.assertTrue(doc[0].to_json())

    def test_get_eps(self):
        sents = read_gold_mrs()
        s = sents[0]
        l = s[0].dmrs().latex()
        self.assertTrue(l)

    def test_generate_latex(self):
        sents = read_gold_mrs()
        smap = {str(s.ident): s for s in sents}
        s = smap['10283']
        self.assertTrue(s.to_latex())

    def test_sent2latex(self):
        txt = 'Everyone is a soul.'
        ghub = GrammarHub()
        s = ghub.parse(txt, "ERG")
        out = s.to_latex()
        for i in range(1, 3):
            self.assertIn('%%% {}'.format(i), out)

    def test_ep_types(self):
        sid = '10598'
        sents = read_gold_mrs()
        smap = {str(s.ident): s for s in sents}
        dobj = smap[sid][0].dmrs().obj()
        eps = dobj.eps()
        for ep in eps:
            if ep.nodeid == 10015:
                self.assertEqual(ep.pred.type, Pred.GRAMMARPRED)
        # access by nodeid
        self.assertEqual(dobj.ep(10015).pred, 'named_rel')

    def test_lelesk_tagging(self):
        sents = read_gold_mrs()
        sents[0].tag(method=TagInfo.MFS)
        self.assertTrue(sents[0].to_xml_str())

    def test_flag_not_matched_concept(self):
        ''' Lexsem should flag the not matched concepts '''
        sid = '10322'
        sents = read_gold_mrs()
        smap = {str(s.ident): s for s in sents}
        sent = smap[sid]
        dmrs = sent[0].dmrs()
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        tagged = doc.sent_map[sid]
        m, n = tag_gold(dmrs, tagged, sent.text)
        self.assertGreater(len(m), 0)

    def test_read_tags(self):
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        for tagged in doc:
            for w, concepts in tagged.wclinks.items():
                actual = {"{}-{}".format(c.clemma, c.tag) for c in concepts}
                self.assertEqual(len(actual), len(concepts), "WARNING: duplicate concept (w={} | c={})".format(w, concepts))

    def test_sent_surface_matching(self):
        print("Test surface matching ...")
        sents = read_gold_mrs()
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        for s in sents:
            tagged = doc.sent_map[str(s.ident)]
            self.assertEqual(tagged.text, s.text)
            # if tagged.text != s.text:
            #     logger.debug("UPDATE sent SET sent = '{}' WHERE sid = {};".format(s.text.replace("'", "''"), s.ident))

    def test_tag_one_sent(self):
        print("Test tagging one sentence")
        sid = '10581'
        sents = read_gold_mrs()
        smap = {str(s.ident): s for s in sents}
        sent = smap[sid]
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        tagged = doc.sent_map[sid]
        if sent.text != tagged.text:
            print("WARNING: Inconsistent")
            print(sent.text)
            print(tagged.text)
        dmrs = sent[0].dmrs()
        # print(sent.to_xml_str())
        m, n = tag_gold(dmrs, tagged, sent.text)
        header("#{}: {}".format(sid, sent.text), 'h0')
        print(sent[0].dmrs())
        header('Concepts')
        for c in tagged.concepts:
            print(c, c.words)
        header('Matched')
        for con, nid, pred in m:
            print("{}::{} => #{}::{}".format(con.tag, con.clemma, nid, pred))
        header("Not matched")
        if n:
            for c in n:
                print(c)
        else:
            print("All was matched.")
        sent.tag(method=TagInfo.MFS)
        xml_str = sent.tag_xml().to_xml_str()
        self.assertTrue(xml_str)
        self.assertIn("<sensegold", xml_str)
        self.assertIn("<sense", xml_str)

    def test_gen_gold(self):
        sents = read_gold_mrs()
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        for s in sents[:5]:
            if len(s) > 0:
                # tag it
                tagged = doc.sent_map[str(s.ident)]
                tag_gold(s[0].dmrs(), tagged, s.text)

    def test_generate_from_gold(self):
        header("Test generating from gold (THIS IS SLOW)")
        sents = read_gold_mrs()
        c = Counter()
        for sent in sents[:3]:
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
        print("Tagging everything ...")
        sents = read_gold_mrs()
        smap = {str(s.ident): s for s in sents}
        # reag tags
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        filter_wrong_senses(doc)
        count_good_bad = Counter()
        perfects = []
        to_be_checked = dd(list)
        tbc_concepts = dd(list)
        concept_count = Counter()
        fix_texts = []
        instances = Counter()
        tag_map = dd(set)
        matched_report = TextReport('data/gold_matched.txt')
        not_matched_report = TextReport('data/gold_notmatched.txt')
        for s in sents:
            # header(s, 'h0')
            sid = str(s.ident)
            if sid not in doc.sent_map:
                raise Exception("Cannot find sentence {}".format(sid))
            elif len(s) == 0:
                logging.warning("Empty sentence: {}".format(s))
            else:
                tagged = doc.sent_map[sid]
                if s.text != tagged.text:
                    fix_texts.append((s.ident, s.text, tagged.text))
                # try to tag ...
                dmrs = s[0].dmrs()
                matched, not_matched = tag_gold(dmrs, tagged, s.text, mode=Lexsem.ROBUST)
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
            tagged = doc.sent_map[str(sent.ident)]
            matched_report.header("#{}: {}".format(sent.ident, sent.text), "h0")
            matched_report.writeline(sent[0].dmrs())
            matched_report.header("Concepts")
            for c, nid, pred in m:
                matched_report.writeline("{} ===> {}:{}".format(c, nid, pred))
            matched_report.writeline()
            matched_report.writeline()
        # report not matched
        not_matched_report.header("By senses", "h0")
        for k, v in concept_count.sorted_by_count():
            sids = ' '.join(["#{}".format(x) for x in tbc_concepts[k]])
            not_matched_report.print("{}: {} | {} => {}".format(k, v, sids, tag_map[k]))
        not_matched_report.header("By sentences", "h0")
        for sid, nm in to_be_checked.items():
            not_matched_report.print("#{}: {}  | {}".format(sid, nm, smap[str(sid)].text))
        # full details
        for sid, nm in to_be_checked.items():
            sent = smap[str(sid)]
            tagged = doc.sent_map[str(sid)]
            not_matched_report.header("#{}: {}".format(sid, sent.text))
            not_matched_report.writeline(sent[0].dmrs())
            for n in nm:
                not_matched_report.writeline(n)

        # for i, t1, t2 in fix_texts:
        #     print(i)
        #     print(t1)
        #     print(t2)
        count_good_bad.summarise()
        instances.summarise()


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
