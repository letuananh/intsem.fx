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
from lelesk import WSDResources
from chirptext.texttaglib import writelines
from collections import defaultdict as dd

##########################################
# CONFIGURATION
##########################################
GRAM_FILE = './data/erg.dat'
ACE_BIN = os.path.expanduser('~/bin/ace')
INPUT_TXT = 'data/speckled.txt'
INPUT_MRS = 'data/spec-erg.txt'
SKIPPED_SENTENCE = 'data/speckled.skipped'
OUTPUT_ISF = 'data/spec-isf.xml'
PRED_DEBUG_DUMP = 'data/speckled_synset.isf'
GOLD_PROFILE = 'data/speckled_synset.human'

prettify_xml = lambda x: xml.dom.minidom.parseString(x).toprettyxml()

def read_data(file_path):
    data = []
    with open(file_path, 'r') as input_file:
        for line in input_file:
            data.append(tuple(line.split()))
    return data

def main():
    print("Loading WordNet ...")
    WSDResources.singleton(True)
    
    print("Reading gold profile")
    golddata = read_data(GOLD_PROFILE)
    sid_gold_map = dd(list)
    for datum in golddata:
        sid_gold_map[datum[0]].append(datum)
    print("Gold map: %s" % [len(sid_gold_map)])
    print("Reading raw data ...")
    # interactive_shell()
    c = Counter()
    items = []
    sentences = []
    skipped = []
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
                skipped.append(line[5:].strip())
                items.append([line])
                input_mrs.readline()
                input_mrs.readline()
                c.count('skip')
                c.count('total')
            else:
                break
    c.summarise() 
    writelines(skipped, SKIPPED_SENTENCE)
    
    #preds = sentences[0].mrs[0].preds()
    #for pred in preds:
    #    print(PredSense.search_pred_string(pred.label, False))
    #exit()
    
    # Process data
    print("Generating XML data ...")
    doc_node = ET.Element('document')
    doc_node.set('name', 'speckled band')
    preds_debug = []
    
    cgold = Counter()
    
    for sent in sentences:
        #print("Processing %s" % (sent.sid + 9999,))
        sent_node = ET.SubElement(doc_node, 'sentence')
        sent_node.set('sid', str(sent.sid))
        text_node = ET.SubElement(sent_node, 'text')
        text_node.text = sent.text
        dmrses_node = ET.SubElement(sent_node, 'dmrses')
        dmrs_xml = ET.fromstring(sent.mrs[0].dmrs_xml(False))
        dmrses = dmrs_xml.findall('dmrs')
        for dmrs in dmrses:
            dmrses_node.append(dmrs)
        # add senseinfo to every preds
        si_node = ET.SubElement(sent_node, 'senses')
        
        # WSD info
        best_candidate_map = {}
        # Store data for debugging purposes
        
        for pred in sent.mrs[0].preds():
            candidates = PredSense.search_pred_string(pred.label, False)
            if candidates:
                #if candidates[0].lemma == 'very':
                 #   print(candidates)
                  #  exit()
                preds_debug.append((sent.sid + 9999, pred.cfrom, pred.cto, str(candidates[0].sid)[1:]+'-'+candidates[0].pos, candidates[0].lemma))
                best_candidate_map[pred_to_key(pred)] = candidates[0]
                sense_node = ET.SubElement(si_node, 'pred')
                #sense_node.set('key', pred_to_key(pred))
                sense_node.set('cfrom', str(pred.cfrom))
                sense_node.set('cto', str(pred.cto))
                sense_node.set('label', str(pred.label))
                for candidate in candidates:
                    candidate_node = ET.SubElement(sense_node, 'sense')
                    candidate_node.set('pos', str(candidate.pos))
                    candidate_node.set('synsetid', str(candidate.sid))
                    candidate_node.set('sensekey', str(candidate.sk))
                    candidate_node.set('lemma', str(candidate.lemma))
                    candidate_node.set('tagcount', str(candidate.tagcount))
        #print(best_candidate_map)
        # Storing best candidates & gold sense
        for dmrs in dmrses_node:
            for node in dmrs.findall('node'):
                # insert gold sense
                goldtags = sid_gold_map[str(sent.sid + 9999)]
                if goldtags:
                    for tag in goldtags:
                        # print(' '.join([str(x) in [tag[1], tag[2], node.get('cfrom'), node.get('cto')]]))
                        if int(tag[1]) == int(node.get('cfrom')) and int(tag[2]) == int(node.get('cto')):
                            gold_node = ET.SubElement(node, 'sensegold')
                            gold_node.set('synset', tag[3])
                            gold_node.set('clemma', tag[4])
                            cgold.count('inserted')
                realpred = node.find('realpred')
                if realpred is not None:
                    # insert mcs
                    key = '-'.join((str(node.get('cfrom')), str(node.get('cto')), str(realpred.get('pos')), str(realpred.get('lemma')), str(realpred.get('sense'))))
                    #print('%s is found' % (key,))
                    if key in best_candidate_map:
                        # print("injecting")
                        candidate = best_candidate_map[key]
                        candidate_node = ET.SubElement(node, 'sense')
                        candidate_node.set('pos', str(candidate.pos))
                        candidate_node.set('synsetid', str(candidate.sid))
                        candidate_node.set('sensekey', str(candidate.sk))
                        candidate_node.set('lemma', str(candidate.lemma))
                        candidate_node.set('tagcount', str(candidate.tagcount))
                #else:
                    #print('%s is not good' % (realpred,))
    
    cgold.summarise()
    print("Dumping preds debug")
    writelines([ '\t'.join([str(i) for i in x]) for x in preds_debug], PRED_DEBUG_DUMP)
        #exit()
    with open(OUTPUT_ISF, 'w') as output_isf:
        print("Making it beautiful ...")
        xml_string = prettify_xml(ET.tostring(doc_node, encoding='utf-8'))
        print("Saving XML data to file ...")
        output_isf.write(xml_string)
    print("All done!")

def pred_to_key(pred):
    pred_obj = Pred.grammarpred(pred.label)
    return '-'.join((str(pred.cfrom), str(pred.cto), str(pred_obj.pos), str(pred_obj.lemma), str(pred_obj.sense)))
    

if __name__ == "__main__":
    main()
