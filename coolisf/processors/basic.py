# -*- coding: utf-8 -*-

'''
Basic Japanese processors

Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
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
            sent.text = ' '.join(t.label for t in sent.shallow.tokens)
            return sent
        else:
            return self.process(Sentence(sent))
