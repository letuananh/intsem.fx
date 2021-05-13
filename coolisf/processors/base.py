# -*- coding: utf-8 -*-

"""
Linguistic processors
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging
import importlib
import threading
from collections import namedtuple


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

ProcessorInfo = namedtuple("ProcessorInfo", ["module_name", "class_name"])


def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Classes
# ----------------------------------------------------------------------

class ProcessorManager(object):

    def __init__(self):
        self.prep_canon_map = {}  # map (module, cls) to an actual prep object
        self.name_map = {}  # map a friendly name to a prep object

    def register(self, friendly_name, module_name, class_name):
        self.name_map[friendly_name] = ProcessorInfo(module_name, class_name)

    def build_prep(self, prep_info, prep_name=""):
        """ Build or retrieve a preprocessor object based on its specs """
        if prep_info not in self.prep_canon_map:
            with threading.Lock():
                module = importlib.import_module(prep_info.module_name)
                cls = getattr(module, prep_info.class_name)
                prep = cls(prep_info, prep_name)
                self.prep_canon_map[prep_info] = prep
        return self.prep_canon_map[prep_info]

    def __getitem__(self, prep_name):
        if prep_name not in self.name_map:
            raise LookupError("Invalid prep_name ({} was provided)".format(prep_name))
        prep_info = self.name_map[prep_name]
        return self.build_prep(prep_info, prep_name)

    @staticmethod
    def from_json(json_data):
        man = ProcessorManager()
        for k, info in json_data.items():
            man.register(k, info["module"], info["class"])
        return man


class Processor(object):
    """ Standard preprocessor structure """

    def __init__(self, info, name=""):
        self.info = info
        self.name = name

    def process(self, text):
        return text
