# -*- coding: utf-8 -*-

''' CoolISF Data Access Package
'''

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

from .corpus import CorpusDAOSQLite
from .tsdb import read_tsdb

__all__ = ['CorpusDAOSQLite', 'read_tsdb']
