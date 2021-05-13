# -*- coding: utf-8 -*-

"""
Basic Japanese processors
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging

from coolisf.shallow import EnglishAnalyser
from coolisf.model import Sentence
from coolisf.morph import Transformer
from .base import Processor


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------

class PostISF(Processor):

    # static
    transformer = Transformer()

    def __init__(self, info, name="isf"):
        super().__init__(info, name)
        # self.transformer = Transformer()

    def process(self, parse):
        getLogger().debug("{} is postprocessing 1 mrs".format(self.name))
        self.transformer.apply(parse)
        getLogger().debug("{} ended".format(self.name))
        return parse


class PrepNLTK(Processor):

    def __init__(self, info, name="nltk"):
        super().__init__(info, name)
        self.parser = EnglishAnalyser()

    def process(self, sent):
        if isinstance(sent, Sentence):
            sent.shallow = self.parser.analyse(sent.text)
            sent.text = ' '.join(t.text for t in sent.shallow.tokens)
            return sent
        else:
            return self.process(Sentence(sent))
