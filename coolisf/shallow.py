# -*- coding: utf-8 -*-

'''
Sentence shallow analyser
Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
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

########################################################################

import os
import logging

import nltk
from nltk.stem import WordNetLemmatizer
from chirptext import texttaglib as ttl
try:
    from chirptext.deko import txt2mecab
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
        msent = txt2mecab(sent).words
        return msent

    def lemmatize(self, words):
        msent = txt2mecab(' '.join(words))
        return [m.reading_hira() for m in msent if not m.is_eos]

    def pos_tag(self, words):
        msent = txt2mecab(' '.join(words))
        return [(m.surface, m.pos3()) for m in msent]

    def analyse(self, sent):
        msent = txt2mecab(sent)
        tsent = ttl.Sentence(msent.surface)
        tsent.import_tokens(msent.words)
        # pos tagging
        for mtk, tk in zip(msent, tsent):
            tk.pos = mtk.pos3()
            tk.lemma = mtk.root
            tk.new_tag(mtk.reading_hira(), tagtype="reading", source=ttl.Tag.MECAB)
        return tsent
