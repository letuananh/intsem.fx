#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>

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

import os
from delphin import itsdb
from collections import namedtuple

GOLD_PROFILE = os.path.expanduser('data/gold')
OUTPUT_FILE = os.path.expanduser('data/gold.out.txt')

class Sentence:
    def __init__(self, sid, text, mrs=None):
        self.sid = sid
        self.text = text
        self.mrs = mrs

def main():
    print("Loading Gold profile ...")
    prof = itsdb.ItsdbProfile(GOLD_PROFILE)
    tbl_item = prof.read_table('item')
    sentences = dict()
    for row in tbl_item:
        iid = row.get('i-id')
        raw_text = row.get('i-input')
        sentences[iid] = Sentence(iid, raw_text)
        # print('%s: %s ' % (iid, raw_text))
    tbl_result = prof.read_table('result')
    for row in tbl_result:
        pid = row.get('parse-id')
        mrs = row.get('mrs')
        if pid not in sentences:
            print('pid %s cannot be found' % pid)
        else:
            sentences[pid].mrs = mrs
#         print('%s: %s ' % (pid, mrs))
    with open(OUTPUT_FILE, 'w') as outfile:
        for sent in sentences.values():
            outfile.write('%s\t%s\t%s\n' % (sent.sid, sent.text, sent.mrs))

if __name__ == "__main__":
    main()