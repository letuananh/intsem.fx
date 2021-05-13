# -*- coding: utf-8 -*-

"""
Advanced Japanese processors
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

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
