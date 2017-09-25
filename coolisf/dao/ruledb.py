# -*- coding: utf-8 -*-

'''
Rule DB for Optimus Engine
@author: Le Tuan Anh
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
import os.path
import logging

from puchikarui import Schema, with_ctx

from coolisf.model import LexItem

########################################################################

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2017, intsem.fx"
__credits__ = []
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

logger = logging.getLogger(__name__)
MY_DIR = os.path.dirname(os.path.realpath(__file__))
RULEDB_INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'init_ruledb.sql')


class ChunkDB(Schema):

    def __init__(self, data_source=':memory:', setup_script=None, setup_file=RULEDB_INIT_SCRIPT):
        Schema.__init__(self, data_source=data_source, setup_script=setup_script, setup_file=setup_file)
        self.add_table('word', ['ID', 'lemma', 'pos', 'flag'], proto=LexItem, id_cols=('ID',))
        self.add_table('parse').add_fields('ID', 'raw', 'wid', 'preds').set_id('ID')

    def get_parses(self, word, ctx):
        parses = ctx.parse.select('wid = ?', (word.ID,))
        if parses:
            word.parses = parses
        return parses

    def flag(self, word, flag, ctx):
        word.flag = flag
        self.word.save(word, columns=('flag',))

    @with_ctx
    def get_words(self, lemma=None, pos=None, flag=None, limit=None, deep_select=True, ctx=None):
        query = []
        params = []
        if lemma:
            query.append("lemma = ?")
            params.append(lemma)
        if pos:
            query.append("pos = ?")
            params.append(pos)
        if flag:
            query.append("flag = ?")
            params.append(flag)
        words = ctx.word.select(" AND ".join(query), params, limit=limit)
        if deep_select:
            for word in words:
                self.get_parses(word, ctx=ctx)
        return words
