# -*- coding: utf-8 -*-

'''
TSDB DAO
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
import json

from delphin import itsdb
from puchikarui import Schema, with_ctx

from coolisf.model import Document, Sentence

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


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def read_tsdb(path):
    prof = itsdb.ItsdbProfile(path)
    doc = Document(name=os.path.dirname(path))
    # Read all sentences
    tbl_item = prof.read_table('item')
    for row in tbl_item:
        iid = row.get('i-id')
        raw_text = row.get('i-input').strip()
        sent = Sentence(text=raw_text, ident=iid)
        doc.add(sent)
    # Read all parses
    tbl_result = prof.read_table('result')
    for row in tbl_result:
        pid = row.get('parse-id')
        mrs = row.get('mrs')
        if pid not in doc.ident_map:
            raise Exception('pid {} cannot be found in provided TSDB profile'.format(pid))
        elif mrs:
            doc.ident_map[pid].add(mrs)
        else:
            raise Exception("Invalid MRS string in provided TSDB profile")
    return doc
