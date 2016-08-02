#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Basic data models

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
	Python documentation:
		https://docs.python.org/
	argparse module:
		https://docs.python.org/3/howto/argparse.html
	PEP 257 - Python Docstring Conventions:
		https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import delphin
from delphin.mrs import simplemrs
from delphin.mrs import dmrx
from delphin.mrs.components import Pred
from chirptext.leutile import StringTool
from chirptext.texttaglib import TagInfo
# from model import Sentence, DMRS

########################################################################

class Sentence:
    def __init__(self, text='', sid=-1):
        self.text = StringTool.strip(text)
        self.sid = sid
        self.mrs = list()
        self.raw_mrs = list()

    def add(self, mrs):
        self.mrs.append(DMRS(StringTool.strip(mrs), self))

    def __str__(self):
        return "%s (%s mrs)" % (self.text, len(self.mrs))


class DMRS:
    def __init__(self, mrs_text, sent=None):
        self.sent = sent
        self.text = mrs_text
        self.mrs_obj = None

    def mrs(self):
        if self.mrs_obj is None:
            self.mrs_obj = simplemrs.loads_one(self.text)
        return self.mrs_obj

    def dmrs_xml(self, pretty_print=False):
        return dmrx.dumps([simplemrs.loads_one(self.text)], pretty_print=pretty_print)

    def surface(self, node):
        if not node or not self.sent:
            return None
        else:
            return self.sent.text[int(node.cfrom):int(node.cto)]

    def clear(self):
        self.mrs_obj = None

    def tagged(self):
        return TaggedSentence(self.sent.text, self.preds())

    def ep_to_taginfo(self, ep):
        nodeid = ep[0]
        pred   = ep[1]
        label  = ep[2]
        args   = ep[3]
        cfrom  = -1
        cto    = -1
        if len(ep) > 4:
            lnk    = ep[4]
            cfrom  = lnk.data[0]
            cto    = lnk.data[1]
        pred_string = delphin.mrs.components.normalize_pred_string(pred.string)
        return TagInfo(cfrom, cto, pred_string)
        
    
    def preds(self):
        return [ self.ep_to_taginfo(x) for x in self.mrs().eps() ]


def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
