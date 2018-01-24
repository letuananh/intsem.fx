# -*- coding: utf-8 -*-

''' Test scripts for the Integrated Semantic Framework
Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# This source code is a part of the Integrated Semantic Framework
# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
# LICENSE: The MIT License (MIT)
#
# Homepage: https://github.com/letuananh/intsem.fx

import os
from chirptext.cli import setup_logging
from .common import TEST_DIR, TEST_DATA


setup_logging(os.path.join(TEST_DIR, 'logging.json'), os.path.join(TEST_DIR, 'logs'))


__all__ = ['TEST_DIR', 'TEST_DATA']
