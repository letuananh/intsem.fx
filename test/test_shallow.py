#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for shallow analyser
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging
from lelesk import LeLeskWSD, LeskCache
from coolisf.shallow import Analyser, EnglishAnalyser, JapaneseAnalyser


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestMain(unittest.TestCase):

    def test_default(self):
        a = Analyser()
        txt = 'Some dogs barked.'
        words = a.tokenize(txt)
        lemmas = a.lemmatize(words)
        tags = a.pos_tag(words)
        tsent = a.analyse(txt)
        self.assertEqual(words, ['Some', 'dogs', 'barked.'])
        self.assertEqual(lemmas, ['Some', 'dogs', 'barked.'])
        self.assertEqual(tags, [('Some', 'n'), ('dogs', 'n'), ('barked.', 'n')])
        twords = [t.text for t in tsent]
        self.assertEqual(twords, ['Some', 'dogs', 'barked.'])
        for t in tsent:
            self.assertEqual(t.text, txt[t.cfrom:t.cto])

    def test_eng(self):
        a = EnglishAnalyser()
        txt = 'Some dogs barked.'
        words = a.tokenize(txt)
        lemmas = a.lemmatize(words)
        tags = a.pos_tag(words)
        tsent = a.analyse(txt)
        self.assertEqual(words, ['Some', 'dogs', 'barked', '.'])
        self.assertEqual(lemmas, ['Some', 'dog', 'bark', '.'])
        self.assertEqual(tags, [('Some', 'DT'), ('dogs', 'NNS'), ('barked', 'VBD'), ('.', '.')])
        twords = [t.text for t in tsent]
        self.assertEqual(twords, ['Some', 'dogs', 'barked', '.'])
        for tk, lm, tg in zip(tsent, lemmas, tags):
            self.assertEqual(tk.text, txt[tk.cfrom:tk.cto])
            self.assertEqual(tk.lemma, lm)
            self.assertEqual(tk.pos, tg[1])

    def test_wsd_shallow(self):
        txt = 'The dogs barked.'
        a = EnglishAnalyser()
        tsent = a.analyse(txt)
        l = LeLeskWSD(dbcache=LeskCache())
        context = [x.lemma for x in tsent]
        cid = 0
        for w in tsent:
            scores = l.lelesk_wsd(w.lemma, tsent.text, context=context)
            if scores:
                # take the best one
                tsent.new_concept(scores[0].candidate.synset.ID, clemma=w.lemma, ID=cid, tokens=[w])
                cid += 1
        tags = {c.tag for c in tsent.concepts}
        self.assertEqual(tags, {'07376731-n', '02084071-n'})

    def test_jpn(self):
        a = JapaneseAnalyser()
        txt = '猫が好きだった。'
        tokens = a.tokenize(txt)
        lemmas = a.lemmatize(tokens)
        self.assertEqual(tokens, ['猫', 'が', '好き', 'だっ', 'た', '。'])
        self.assertEqual(lemmas, ['猫', 'が', '好き', 'だ', 'た', '。'])
        # test POS tagger
        tags = a.pos_tag(tokens)
        expected = [('猫', '名詞-一般'), ('が', '助詞-格助詞-一般'), ('好き', '名詞-形容動詞語幹'), ('だっ', '助動詞'), ('た', '助動詞'), ('。', '記号-句点'), ('EOS', '')]
        self.assertEqual(tags, expected)
        tsent = a.analyse(txt)
        twords = [t.text for t in tsent]
        self.assertEqual(twords, ['猫', 'が', '好き', 'だっ', 'た', '。'])


# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
