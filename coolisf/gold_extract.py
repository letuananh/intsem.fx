#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Extract data from a TSDB profile and write to a text file
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

import os
from collections import namedtuple
from delphin import itsdb
from fuzzywuzzy import fuzz

from chirptext.leutile import Counter, Timer, FileTool, StringTool

########################################################################

GOLD_PROFILE = FileTool.abspath('./data/gold')
OUTPUT_FILE  = FileTool.abspath('./data/gold.out.txt')
RAW_TEXT     = FileTool.abspath('./data/speckled.txt')
GOLD_RAW     = FileTool.abspath('./data/gold.raw.txt')

class Sentence:
    def __init__(self, sid, text, mrs=''):
        self.sid = sid
        self.ntuid = None
        self.text = text
        self.mrs = mrs

def main():
    t = Timer()

    t.start("Loading raw text from [%s] ..." % (RAW_TEXT,))
    raw_sentences = []
    with open(RAW_TEXT, 'r') as rawtext:
        lines = rawtext.readlines()
        for line in lines:
            parts = line.strip().split('\t')
            raw_sentences.append(Sentence(parts[0], parts[1]))
    print("Number of raw sentences: %s" % len(raw_sentences))
    t.end("Raw text has been loaded.")
    
    t.start("Loading Gold Profile from [%s] ..." % (GOLD_PROFILE,))
    prof = itsdb.ItsdbProfile(GOLD_PROFILE)

    # Read all items
    tbl_item = prof.read_table('item')
    gold_sentences = []
    sentences_map = dict()
    with open(GOLD_RAW, 'w') as gold_raw:
        for row in tbl_item:
            iid = row.get('i-id')
            raw_text = row.get('i-input').strip()
            sentences_map[iid] = Sentence(iid, raw_text)
            gold_sentences.append(sentences_map[iid])
            gold_raw.write('%s\n' % raw_text)
            # print('%s: %s ' % (iid, raw_text))

    # Read all parse results
    tbl_result = prof.read_table('result')
    for row in tbl_result:
        pid = row.get('parse-id')
        mrs = row.get('mrs')
        if pid not in sentences_map:
            print('pid %s cannot be found' % pid)
        else:
            sentences_map[pid].mrs = StringTool.to_str(mrs)
    t.end('Gold profile has been loaded.')

    # Compare raw sentences with sentences from ITSDB
    c = Counter()
    for i in range(len(raw_sentences)):
        s = gold_sentences[i]
        rs = raw_sentences[i]
        ratio = fuzz.ratio(rs.text, s.text)
        c.count("TOTAL")
        if ratio < 95:
            print("[%s] != [%s]" % (rs.text, s.text))
            c.count('MISMATCH')
        else:
            s.ntuid = rs.sid
            if ratio < 100:
                c.count("FUZZMATCHED")
            else:
                c.count("MATCHED")
    c.summarise()

    # Write found sentences and parse results to a text file
    t.start("Writing found sentences and parse results to [%s] ..." % (OUTPUT_FILE))
    with open(OUTPUT_FILE, 'w') as outfile:
        for sent in gold_sentences:
            outfile.write('%s\t%s\t%s\t%s\n' % (sent.ntuid, sent.sid, sent.text, sent.mrs))
    t.end("Data has been written to file.")
    
    # Verification
    t.start("Verifying file [%s] ..." % (OUTPUT_FILE,))
    with open(OUTPUT_FILE, 'r') as testfile:
        for line in testfile:
            parts = line.split('\t')
            if len(parts) != 4:
                print("WARNING: INVALID LINE")
    t.end("Output file has been verified.")

    print("All done!")
    
if __name__ == "__main__":
    main()
