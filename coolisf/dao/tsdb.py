# -*- coding: utf-8 -*-

"""
TSDB DAO
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import os.path
import logging

from delphin import itsdb

from coolisf.model import Document, Sentence


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

logger = logging.getLogger(__name__)
MY_DIR = os.path.dirname(os.path.realpath(__file__))


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def read_tsdb(path, name=None, title=None):
    """ Read a TSDB profile in ISF format """
    prof = itsdb.ItsdbProfile(path)
    if name is None:
        name = os.path.basename(path)
    if title is None:
        title = name
    doc = Document(name=name, title=title)
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
