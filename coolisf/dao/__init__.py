# -*- coding: utf-8 -*-

''' CoolISF Data Access Package
Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# This source code is a part of the Integrated Semantic Framework
# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
# LICENSE: The MIT License (MIT)
#
# Homepage: https://github.com/letuananh/intsem.fx

from .corpus import CorpusDAOSQLite
from .tsdb import read_tsdb

__all__ = ['CorpusDAOSQLite', 'read_tsdb']
