# -*- coding: utf-8 -*-

"""
Sentence shallow analyser
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging

import nltk
from nltk.stem import WordNetLemmatizer
from texttaglib.chirptext import texttaglib as ttl
try:
    from texttaglib.chirptext.deko import txt2mecab
    from texttaglib.chirptext.deko import tokenize as deko_tokenize
except:
    logging.warning("Deko cannot be imported. JapaneseAnalyser will not function properly")


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Classes
# -------------------------------------------------------------------------------

class Analyser(object):

    def __init__(self, lang=None):
        self.lang = lang  # use ISO 639-2 three-letter codes

    def tokenize(self, text):
        return text.split()

    def lemmatize(self, words):
        return words

    def pos_tag(self, words):
        # everything is a noun
        return [(w, 'n') for w in words]

    def analyse(self, text):
        tsent = ttl.Sentence(text)
        words = self.tokenize(text)
        tsent.import_tokens(words)
        for tk, lm in zip(tsent, self.lemmatize(words)):
            tk.lemma = lm
        for tk, pos in zip(tsent, [pos for w, pos in self.pos_tag(words)]):
            tk.pos = pos
        return tsent


class EnglishAnalyser(Analyser):

    wnl = WordNetLemmatizer()

    def __init__(self):
        super().__init__(lang="eng")

    def tokenize(self, sent):
        return nltk.word_tokenize(sent)

    def pos2wnpos(self, pos):
        if pos:
            p = pos[0].lower()
            if p == 'j':
                return 'a'
            if p in 'svarn':
                return p
        return 'n'  # default is a noun

    def lemmatize(self, words):
        return [self.wnl.lemmatize(w, pos=self.pos2wnpos(p)) for w, p in self.pos_tag(words)]

    def pos_tag(self, words):
        return nltk.pos_tag(words)

    def analyse(self, text):
        tsent = ttl.Sentence(text)
        words = self.tokenize(text)
        tsent.import_tokens(words)
        for tk, pos in zip(tsent, [pos for w, pos in self.pos_tag(words)]):
            tk.pos = pos
            tk.lemma = self.wnl.lemmatize(tk.text, pos=self.pos2wnpos(pos))
        return tsent


class JapaneseAnalyser(Analyser):

    def __init__(self):
        super().__init__(lang="jpn")

    def tokenize(self, sent):
        return deko_tokenize(sent)

    def lemmatize(self, words):
        msent = txt2mecab(' '.join(words))
        return [m.root for m in msent if not m.is_eos]

    def pos_tag(self, words):
        msent = txt2mecab(' '.join(words))
        return [(m.surface, m.pos3()) for m in msent]

    def analyse(self, sent):
        msent = txt2mecab(sent)
        return msent.to_ttl()
