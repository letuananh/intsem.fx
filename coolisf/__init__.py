# -*- coding: utf-8 -*-

'''
Python implementation of Integrated Semantic Framework

`coolisf` is read `kul-eye-es-ef` officially

'''

# Latest version can be found at https://github.com/letuananh/intsem.fx
#
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

from .__version__ import __author__, __email__, __copyright__, __maintainer__
from .__version__ import __credits__, __license__, __description__, __url__
from .__version__ import __version_major__, __version_long__, __version__, __status__

# disable future warning in pydelphin 0.6.0
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

from .lexsem import Lexsem, tag_gold
from .ghub import GrammarHub
from .config import read_config

__all__ = ['GrammarHub', 'Lexsem', 'tag_gold', 'read_config',
           "__version__", "__author__", "__description__", "__copyright__"]
