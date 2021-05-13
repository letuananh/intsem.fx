# -*- coding: utf-8 -*-

""" Test scripts for the Integrated Semantic Framework
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
from texttaglib.chirptext.cli import setup_logging

TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')
setup_logging(os.path.join(TEST_DIR, 'logging.json'), os.path.join(TEST_DIR, 'logs'))


__all__ = ['TEST_DIR', 'TEST_DATA']
