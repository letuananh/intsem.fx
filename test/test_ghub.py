#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for ghub
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from texttaglib.chirptext import header
import chirptext.texttaglib as ttl
from coolisf import GrammarHub
from coolisf.model import Document
from coolisf.dao import CorpusDAOSQLite


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestGrammarHub(unittest.TestCase):

    db = CorpusDAOSQLite(":memory:", "memdb")
    ghub = GrammarHub()

    def test_erg(self):
        db = self.db
        with self.db.ctx() as ctx:
            # create sample sentence
            corpus = db.create_corpus('test', ctx=ctx)
            doc = corpus.new('testdoc')
            db.save_doc(doc, ctx=ctx)
            s = self.ghub.ERG.parse("It works.", parse_count=1)
            j1 = s[0].dmrs().json()
            s.docID = doc.ID
            db.save_sent(s, ctx=ctx)
            # select back
            sent = db.get_sent(s.ID, ctx=ctx)
            j2 = sent[0].dmrs().json()
            self.assertEqual(j1, j2)

    def test_extra_args(self):
        output = self.ghub.ERG.parse("self sufficient", extra_args=['-r', 'root_formal'])
        self.assertEqual(len(output), 0)
        output = self.ghub.ERG.parse("self sufficient", extra_args=['-r', 'root_frag'])
        self.assertTrue(len(output))

    def test_ghub_to_corpus(self):
        db = self.db
        with self.db.ctx() as ctx:
            # create sample sentence
            corpus = db.create_corpus('test', ctx=ctx)
            doc = corpus.new('testdoc')
            db.save_doc(doc, ctx=ctx)
            s = self.ghub.parse("Abraham's dog barked.", "ERG", pc=1)
            s.docID = doc.ID
            db.save_sent(s, ctx=ctx)
            # select back
            sent = db.get_sent(s.ID, ctx=ctx)
            self.assertIsNotNone(sent)
            self.assertTrue(len(sent))

    def test_prep_jp(self):
        deko = self.ghub.preps['deko']
        sent_ttl = deko.process('猫がすきです。').shallow
        doc_ttl = ttl.Document('neko', '~/tmp/')
        sent_ttl.ID = 1
        doc_ttl.add_sent(sent_ttl)
        doc_ttl.write_ttl()
        self.assertIsInstance(sent_ttl, ttl.Sentence)

    def test_prep_en(self):
        np = self.ghub.preps['nltk']
        doc = Document()
        doc_ttl = ttl.Document('fun_nltk', 'data')
        with open('data/tsdb/skeletons/fun.txt') as infile:
            for idx, l in enumerate(infile):
                s = doc.new(l, str(idx + 1))
                print(np.process(s).shallow.to_json())
                sent_ttl = s.shallow
                sent_ttl.ID = idx
                doc_ttl.add_sent(sent_ttl)
        print(doc[0].shallow.to_json())

    def test_all_grammars(self):
        header("Verify available grammars (JACY/VRG/ERG)")
        for n in ('JACY', 'VRG', 'ERG'):
            self.assertIn(n, self.ghub.names)

    def test_grammar_names(self):
        gm = self.ghub.available
        self.assertEqual(gm['JACYMC'], 'JACY/MeCab')

    def test_config(self):
        erg = self.ghub.ERG
        self.assertIsNotNone(erg)

    def test_parse_cache(self):
        ERG = self.ghub.ERG
        txt = "I saw a girl with a telescope."
        ERG.parse(txt, 5)
        # with extra args
        ERG.parse(txt, 10, ['-r', 'root_robust'])
        # test retrieving
        s = ERG.cache.load(txt, ERG.name, 5, None)
        self.assertIsNotNone(s)
        self.assertEqual(len(s), 5)
        s = ERG.cache.load(txt, ERG.name, 10, '-r root_robust')
        self.assertIsNotNone(s)
        self.assertEqual(len(s), 10)
        # test parse many
        texts = ['I eat.', 'I drink.']
        pc = 10
        extra_args = ['-r', 'root_robust']
        sents = ERG.parse_many(texts, parse_count=pc, extra_args=extra_args)
        for sent in sents:
            self.assertGreater(len(sent), 0)
            cached = ERG.cache.load(sent.text, ERG.name, pc, ' '.join(extra_args))
            self.assertIsNotNone(cached)

    def test_parse_iterative(self):
        texts = ['I eat.', 'I drink.', 'I study.', 'I sleep.']
        parses = self.ghub.ERG.parse_many_iterative(texts, ignore_cache=True)
        for text, sent in zip(texts, parses):
            self.assertIsNotNone(sent)
            self.assertEqual(text, sent.text)
            self.assertGreater(len(sent), 0)

    def test_isf_cache(self):
        txt = "I saw a girl with a telescope."
        grm = "ERG"
        pc = 5
        tagger = "MFS"
        s = self.ghub.parse_json(txt, grm, pc, tagger)
        s = self.ghub.cache.load(txt, grm, pc, tagger)
        self.assertIsNotNone(s)
        self.assertEqual(len(s['parses']), 5)


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
