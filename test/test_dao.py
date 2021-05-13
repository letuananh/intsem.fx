#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test DAO
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging
import unittest

from coolisf import GrammarHub
from coolisf.dao import read_tsdb
from coolisf.dao.ruledb import LexRuleDB, parse_lexunit, PredInfo, RulePred
from coolisf.model import LexUnit, RuleInfo
from coolisf.dao.textcorpus import RawCollection

# -----------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------

from test import TEST_DATA


def getLogger():
    return logging.getLogger(__name__)


# -----------------------------------------------------------------------
# TEST SCRIPTS
# -----------------------------------------------------------------------

class TestTSDBDAO(unittest.TestCase):

    def test_read_tsdb(self):
        doc = read_tsdb('data/gold')
        self.assertTrue(doc)
        self.assertTrue(len(doc))


class TestRawData(unittest.TestCase):

    def test_no_metadata(self):
        colpath = os.path.join(TEST_DATA, 'rawcol1')
        col = RawCollection(colpath)
        self.assertEqual(col.name, 'rawcol1')
        self.assertEqual(col.title, '')
        corpuses = col.get_corpuses()
        self.assertEqual(len(corpuses), 2)
        corpus_names = {c.name for c in corpuses}
        self.assertEqual(corpus_names, {'cor1', 'cor2'})
        cor1 = corpuses['cor1']
        cor2 = corpuses['cor2']
        cor1_docs = cor1.get_documents()
        cor2_docs = cor2.get_documents()
        cor1_docnames = {d.name for d in cor1_docs}
        cor2_docnames = {d.name for d in cor2_docs}
        self.assertEqual(cor1_docnames, {'doc1', 'doc2'})
        self.assertEqual(cor2_docnames, {'file1', 'file2'})
        sents = set()
        for corpus in corpuses:
            for doc in corpus.get_documents():
                for sent in doc.read_sentences():
                    sents.add(sent)
        sent_texts = {s.text for s in sents}
        expected = {'It rains.', 'I give a book to Mary.', 'The cathedral and the bazaar', 'It works.', 'Coding is fun.', 'The dog barked.', 'Linux is an operating system.', 'I give Mary a book.'}
        self.assertEqual(sent_texts, expected)

    def test_with_metadata(self):
        colpath = os.path.join(TEST_DATA, 'rawcol2')
        col = RawCollection(colpath)
        self.assertEqual(col.name, 'rawcol2')
        self.assertEqual(col.title, 'Raw Collection 2')
        corpuses = col.get_corpuses()
        self.assertEqual(len(corpuses), 2)
        cor1 = corpuses['cor1']
        cor2 = corpuses['cor2']
        self.assertEqual(cor1.title, 'Raw Corpus 1')
        self.assertEqual(cor2.title, 'Raw Corpus 2')
        cor1_docs = cor1.get_documents()
        cor2_docs = cor2.get_documents()
        cor1_docnames = {d.name for d in cor1_docs}
        cor2_docnames = {d.name for d in cor2_docs}
        self.assertEqual(cor1_docnames, {'doc1', 'doc2'})
        self.assertEqual(cor2_docnames, {'file1', 'file2'})
        # verify sentence ID in cor2 (which is formatted in TSV)
        cor1_ids = set()
        for d in cor1_docs:
            for s in d.read_sentences():
                cor1_ids.add(s.ident)
        self.assertEqual(cor1_ids, {'col2-cor1-doc1-1', 'col2-cor1-doc1-2', 'col2-cor1-doc2-1', 'col2-cor1-doc2-2'})
        # verify all available sentences
        # cor3 and the 3rd sentence in each corpus should not be included
        sents = set()
        for corpus in corpuses:
            for doc in corpus.get_documents():
                for sent in doc.read_sentences():
                    sents.add(sent)
        sent_texts = {s.text for s in sents}
        expected = {'It rains.', 'I give a book to Mary.', 'The cathedral and the bazaar', 'It works.', 'Coding is fun.', 'The dog barked.', 'Linux is an operating system.', 'I give Mary a book.'}
        self.assertEqual(sent_texts, expected)


class TestRuleDB(unittest.TestCase):

    ghub = GrammarHub()
    rdb = LexRuleDB(':memory:')

    def get_constructions(self):
        return [LexUnit(lemma='emergence', pos='n', synsetid='00044455-n'),
                LexUnit(lemma='green tea', pos='n', synsetid='07935152-n'),
                LexUnit(lemma='look up', pos='v', synsetid='00877083-v'),
                LexUnit(lemma='emergent', pos='a', synsetid='00003553-a'),
                LexUnit(lemma='Sherlock Holmes', pos='n', synsetid='09604451-n'),
                LexUnit(lemma='Robin Hood', pos='n', synsetid='10535047-n'),
                LexUnit(lemma='Sinbad the Sailor', pos='n', synsetid='09604706-n'),
                LexUnit(lemma='Olympian Games', pos='n', synsetid='00516720-n'),
                LexUnit(lemma='Nemean Games', pos='n', synsetid='00516559-n'),
                LexUnit(lemma='quickly', pos='r', synsetid='00085811-r')]

    def generate_rdb(self, ctx):
        constructions = self.get_constructions()
        # generate rules
        self.rdb.generate_rules(constructions, lambda x: parse_lexunit(x, self.ghub.ERG), ctx=ctx)
        # generate rule head
        for lu in ctx.lexunit.select():
            self.rdb.get_lexunit(lu, ctx=ctx)

    def test_add_lexunit(self):
        lu = LexUnit(lemma='emergence', pos='n', synsetid='00044455-n')
        with self.rdb.ctx() as ctx:
            lu.ID = ctx.lexunit.save(lu)
            self.rdb.flag(lu, LexUnit.GOLD, ctx=ctx)

    def test_add_stuff(self):
        constructions = self.get_constructions()
        with self.rdb.ctx() as ctx:
            self.generate_rdb(ctx)
            # verification
            tea_rules = self.rdb.find_ruleinfo_by_head('_tea_n_1', restricted=False, ctx=ctx)
            self.assertTrue(len(tea_rules))
            for rinfo in tea_rules:
                self.assertTrue(rinfo.lid)
                self.assertTrue(rinfo.rid)
                self.assertEqual(rinfo.head, '_tea_n_1')
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

    def test_find_rule_smart(self):
        with self.rdb.ctx() as ctx:
            self.generate_rdb(ctx)
            s = self.ghub.ERG.parse('Sherlock Holmes drink green tea.')
            print(s)
            layout = s[0].dmrs().layout
            getLogger().debug("Nodes: {}".format([str(n.pred) for n in layout.nodes]))
            ruleinfos = self.rdb.find_ruleinfo(layout.nodes, restricted=False, ctx=ctx)
            getLogger().debug("Found {} rules".format(len(ruleinfos)))
            for ri in ruleinfos:
                lu = ctx.lexunit.by_id(ri.lid)
                lu = self.rdb.get_lexunit(lu, ctx=ctx)
                print("Potential: {} -> {}".format(ri, lu))

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
