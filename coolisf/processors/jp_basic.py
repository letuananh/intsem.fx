# -*- coding: utf-8 -*-

"""
Basic Japanese processors
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging

from coolisf.model import Sentence
from .base import Processor

try:
    from texttaglib.chirptext.deko import wakati
    from coolisf.shallow import JapaneseAnalyser
except:
    logging.warning('chirptext.deko cannot be imported. JNLP mode is disabled')


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------

class PrepDeko(Processor):

    def __init__(self, info, name="deko"):
        super().__init__(info, name)
        self.parser = JapaneseAnalyser()

    def process(self, sent):
        if isinstance(sent, Sentence):
            sent.shallow = self.parser.analyse(sent.text)
            sent.text = ' '.join(t.text for t in sent.shallow.tokens)
            return sent
        else:
            return self.process(Sentence(sent))


class PrepMeCab(Processor):

    def __init__(self, info, name="mecab"):
        super().__init__(info, name)

    def process(self, sent):
        if isinstance(sent, Sentence):
            sent.text = wakati(sent.text)
            return sent
        else:
            return wakati(sent)
