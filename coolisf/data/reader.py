# -*- coding: utf-8 -*-

"""
Data reader
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

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
