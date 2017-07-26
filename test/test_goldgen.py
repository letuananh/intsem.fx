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
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

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
from coolisf.lexsem import tag_gold
from coolisf.gold_extract import extract_tsdb_gold
from coolisf.gold_extract import read_gold_mrs


#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_GOLD_DIR = 'data'

#-------------------------------------------------------------------------------
# DATA STRUCTURES
#-------------------------------------------------------------------------------


class TestMainApp(unittest.TestCase):

    def test_read_tsdb(self):
        gold = extract_tsdb_gold()
        print(gold)

    def test_read_gold_mrses(self):
        sents = read_gold_mrs()
        self.assertEqual(len(sents), 599)
        self.assertEqual(len(sents[0]), 1)
        self.assertTrue(sents[0].parses[0].mrs())

    def test_read_gold_tags(self):
        doc = TaggedDoc(TEST_GOLD_DIR, 'gold').read()
        self.assertEqual(len(doc), 599)

    def test_get_eps(self):
        sents = read_gold_mrs()
        s = sents[0]
        self.assertTrue(s[0].dmrs().obj().eps())

    def test_ep_types(self):
        sid = '10598'
        sents = read_gold_mrs()
        smap = {str(s.sid): s for s in sents}
        dobj = smap[sid][0].dmrs().obj()
        eps = dobj.eps()
        # print("GRAMMARPRED", Pred.GRAMMARPRED)  #  0
        # print("REALPRED", Pred.REALPRED)        #  1
        # print("STRINGPRED", Pred.STRINGPRED)    #  2
        for ep in eps:
            if ep.nodeid == 10015:
                # print(ep.nodeid, ep.pred, ep.pred.type)
                self.assertEqual(ep.pred.type, Pred.GRAMMARPRED)
        # access by nodeid
        self.assertEqual(dobj.ep(10015).pred, 'named_rel')

    def test_lelesk_tagging(self):
        sents = read_gold_mrs()
        sents[0].tag(method=TagInfo.MFS)
        self.assertTrue(sents[0].to_xml_str())

    def test_tag_one_sent(self):
        sid = '10329'
        sents = read_gold_mrs()
        smap = {str(s.sid): s for s in sents}
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
            print(con.tag, nid, pred)
        header("not matched")
        for c in n:
            print(c)
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
                tagged = doc.sent_map[str(s.sid)]
                tag_gold(s[0].dmrs(), tagged, s.text)

    def test_tagging_all(self):
        sents = read_gold_mrs()
        smap = {str(s.sid): s for s in sents}
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
            sid = str(s.sid)
            if sid not in doc.sent_map:
                raise Exception("Cannot find sentence {}".format(sid))
            elif len(s) == 0:
                logging.warning("Empty sentence: {}".format(s))
            else:
                tagged = doc.sent_map[sid]
                if s.text != tagged.text:
                    fix_texts.append((s.sid, s.text, tagged.text))
                # try to tag ...
                dmrs = s[0].dmrs()
                matched, not_matched = tag_gold(dmrs, tagged, s.text)
                if not not_matched:
                    count_good_bad.count("Perfect")
                    perfects.append((s, matched))
                else:
                    for nm in not_matched:
                        tag_map[nm.tag].add(nm.clemma)
                        tbc_concepts[nm.tag].append(s.sid)
                        concept_count.count(nm.tag)
                        instances.count('instances')
                    to_be_checked[s.sid].append(nm)
                    count_good_bad.count("To be checked")
        # report matched
        for sent, m in perfects:
            tagged = doc.sent_map[str(sent.sid)]
            matched_report.header("#{}: {}".format(sent.sid, sent.text), "h0")
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


GOLD_WRONG = {
    '02108026-v': [10109, 10114, 10178, 10593],  # => {'have'}
    '00066781-r': [10405, 10498, 10501],  # => {'in front'}
    '01554230-a': [10468, 10582],  # => {'such'}
    '01712704-v': [10061, 10265, 10358, 10384],  # => {'do'}
    '01188342-v': [10292],  # => {'be full'}
}


def filter_wrong_senses(doc):
    for sent in doc:
        to_remove = []
        for c in sent.concepts:
            if c.tag[0] in '=!':
                c.tag = c.tag[1:]
            if c.tag in GOLD_WRONG and int(sent.ID) in GOLD_WRONG[c.tag]:
                to_remove.append(c)
        for c in to_remove:
            sent.concept_map.pop(c.cid)


#-------------------------------------------------------------------------------
# MAIN
#-------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
