# -*- coding: utf-8 -*-

'''
Advanced Japanese processors

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

from texttaglib.chirptext import TextReport

from coolisf.model import Sentence
from .base import Processor
try:

    from texttaglib.chirptext.deko import wakati
    from coolisf.shallow import JapaneseAnalyser
    from jamdict import Jamdict
    from jamdict.tools import dump_result
except:
    logging.warning('jamdict package cannot be found. Jamdict analyser will be disabled.')


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------

class PrepJam(Processor):

    def __init__(self, info, name="jam"):
        super().__init__(info, name)
        self.parser = JapaneseAnalyser()
        self.jam = Jamdict()

    def process(self, sent):
        if isinstance(sent, Sentence):
            ttl_sent = self.parser.analyse(sent.text)
            # lookup each token in the dictionary
            for idx, token in enumerate(ttl_sent):
                if not token.lemma:
                    continue
                result = self.jam.lookup(token.lemma, strict_lookup=True)
                if result.entries or result.chars:
                    ids = []
                    for e in result.entries:
                        ids.append('jam::{}'.format(e.idseq))
                    # for c in result.chars:
                    #     ids.append('jam:char:{}'.format(c.literal))
                    nc = ttl_sent.new_concept(tag=';'.join(ids), clemma=token.text, tokens=[token])
                    # comment = TextReport.string()
                    # dump_result(result, report=comment)
                    # nc.comment = comment.content()
                    nc.comment = result.text(compact=False, no_id=True, with_chars=False)
            sent.shallow = ttl_sent
            sent.text = ' '.join(t.text for t in sent.shallow.tokens)
            return sent
        else:
            return self.process(Sentence(sent))
