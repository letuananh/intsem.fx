# -*- coding: utf-8 -*-

'''
Linguistic processors

Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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
        ''' Build or retrieve a preprocessor object based on its specs '''
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
    ''' Standard preprocessor structure '''

    def __init__(self, info, name=""):
        self.info = info
        self.name = name

    def process(self, text):
        return text
