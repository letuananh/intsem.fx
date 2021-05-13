# -*- coding: utf-8 -*-

"""
Configuration helper
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging

from texttaglib.chirptext import FileHelper, AppConfig
from coolisf.common import write_file
from coolisf.data import read_config_template

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

MY_DIR = os.path.dirname(__file__)
__isf_home = os.environ.get('ISF_HOME', MY_DIR)
__app_config = AppConfig('coolisf', mode=AppConfig.JSON, working_dir=__isf_home)


def getLogger():
    return logging.getLogger(__name__)


def _get_config_manager():
    """ Internal function for retrieving application config manager object
    Don't use this directly, use read_config() method instead
    """
    return __app_config


def read_config():
    if not __app_config.config and not __app_config.locate_config():
        # need to create a config
        config_dir = FileHelper.abspath('~/.coolisf')
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        cfg_loc = os.path.join(config_dir, 'config.json')
        default_config = read_config_template()
        getLogger().warning("CoolISF configuration file could not be found. A new configuration file will be generated at {}".format(cfg_loc))
        getLogger().debug("Default config: {}".format(default_config))
        write_file(path=cfg_loc, content=default_config)
    config = __app_config.config
    return config
