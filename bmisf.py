# -*- coding: utf-8 -*-

''' Demo script on how to use the ISF as a package
'''

# This source code is a part of the Integrated Semantic Framework
# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
# LICENSE: The MIT License (MIT)
#
# Homepage: https://github.com/letuananh/intsem.fx

import logging

from chirptext import texttaglib as ttl
from coolisf.ghub import GrammarHub

# Sample script for benchmarking
ghub = GrammarHub()
sent = ghub.parse('I give a book to him.', 'ERG', tagger=ttl.Tag.LELESK, ignore_cache=True)
for reading in sent:
    logging.debug(reading.mrs())
