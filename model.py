#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Le Tuan Anh <tuananh.ke@gmail.com>

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

from delphin.codecs import simplemrs
from delphin.codecs import dmrx
from delphin.mrs.components import Pred
from chirptext.leutile import StringTool
from chirptext.texttaglib import TagInfo
# from model import Sentence, DMRS

class Sentence:
    def __init__(self, text='', sid=-1):
        self.text = StringTool.strip(text)
        self.sid = sid
        self.mrs = list()

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

    def preds(self):
        return [TagInfo(x.cfrom, x.cto, Pred.normalize_pred_string(x.pred.string)) for x in self.mrs().nodes]


def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
