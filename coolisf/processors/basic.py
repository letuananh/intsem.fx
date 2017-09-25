# -*- coding: utf-8 -*-

'''
Basic Japanese processors

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    ACE:
        http://moin.delph-in.net/AceOptions
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import logging


from coolisf.shallow import EnglishAnalyser
from coolisf.model import Sentence
from coolisf.morph import Transformer
from .base import Processor


##########################################
# CONFIGURATION
##########################################

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

########################################################################


class PostISF(Processor):

    def __init__(self, info, name="isf"):
        super().__init__(info, name)
        self.transformer = Transformer()

    def process(self, parse):
        self.transformer.apply(parse)
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