# -*- coding: utf-8 -*-

'''
Data reader
Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2018, Le Tuan Anh <tuananh.ke@gmail.com>
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
import logging
from coolisf.common import read_file

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

MY_DIR = os.path.dirname(__file__)
CCBY30_PATH = os.path.join(MY_DIR, 'CCBY30_template.txt.gz')
CONFIG_JSON_TEMPLATE = os.path.join(MY_DIR, 'config.template.json.gz')


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# functions
# -------------------------------------------------------------------------------

def read_ccby30():
    getLogger().debug("Reading CCBY30 license text from {}".format(CCBY30_PATH))
    return read_file(CCBY30_PATH)


def read_config_template():
    getLogger().debug("Reading CCBY30 license text from {}".format(CONFIG_JSON_TEMPLATE))
    return read_file(CONFIG_JSON_TEMPLATE)
