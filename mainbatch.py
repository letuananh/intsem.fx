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

from delphin.interfaces import ace
from delphin.mrs.components import Pred
from chirptext.leutile import StringTool
from model import Sentence
from util import PredSense
from chirptext.leutile import Counter
import xml.etree.ElementTree as ET
import xml.dom.minidom

##########################################
# CONFIGURATION
##########################################
GRAM_FILE = './data/erg.dat'
ACE_BIN = os.path.expanduser('~/bin/ace')
INPUT_TXT = 'data/speckled.txt'
INPUT_MRS = 'data/speckled.out'
OUTPUT_ISF = 'data/speckled.isf'

prettify_xml = lambda x: xml.dom.minidom.parseString(x).toprettyxml()

def main():
    print("Integrated Semantic Framework has been loaded.")
    # interactive_shell()
    c = Counter()
    items = []
    sentences = []
    with open(INPUT_MRS, 'r') as input_mrs:
        current_sid = 0
        while True:
            current_sid += 1
            line = input_mrs.readline()
            if line.startswith('SENT'):
                mrs_line = input_mrs.readline()
                items.append([line, mrs_line])
                s = Sentence(line[5:], sid=current_sid)
                s.add(mrs_line)
                sentences.append(s)
                input_mrs.readline()
                input_mrs.readline()
                c.count('sent')
                c.count('total')
            elif line.startswith('SKIP'):
                items.append([line])
                input_mrs.readline()
                input_mrs.readline()
                c.count('skip')
                c.count('total')
            else:
                break
    c.summarise() 
    
    # Process data
    print("Generating XML data ...")
    doc_node = ET.Element('document')
    doc_node.set('name', 'speckled band')
    for sent in sentences:
        sent_node = ET.SubElement(doc_node, 'sentence')
        sent_node.set('sid', str(sent.sid))
        text_node = ET.SubElement(sent_node, 'text')
        text_node.text = sent.text
        dmrses_node = ET.SubElement(sent_node, 'dmrses')
        dmrs_xml = ET.fromstring(sent.mrs[0].dmrs_xml(False))
        dmrses = dmrs_xml.findall('dmrs')
        for dmrs in dmrses:
            dmrses_node.append(dmrs)
    with open(OUTPUT_ISF, 'w') as output_isf:
        print("Making it beautiful ...")
        xml_string = prettify_xml(ET.tostring(doc_node, encoding='utf-8'))
        print("Saving XML data to file ...")
        output_isf.write(xml_string)
    print("All done!")

if __name__ == "__main__":
    main()
