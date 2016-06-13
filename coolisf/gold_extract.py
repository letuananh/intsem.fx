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
import datetime
from collections import namedtuple
from collections import defaultdict as dd
import xml.etree.ElementTree as ET
import xml.dom.minidom

from delphin import itsdb
from delphin.interfaces import ace
from delphin.mrs.components import Pred

from fuzzywuzzy import fuzz

from chirptext.leutile import FileTool
from chirptext.leutile import Timer
from chirptext.leutile import StringTool
from chirptext.leutile import Counter
from chirptext.texttaglib import writelines

from coolisf.model import Sentence
from coolisf.util import PredSense

##########################################
# CONFIGURATION
##########################################

GOLD_PROFILE = FileTool.abspath('./data/gold')
OUTPUT_FILE  = FileTool.abspath('./data/gold.out.txt')
RAW_TEXT     = FileTool.abspath('./data/speckled.txt')
GOLD_RAW     = FileTool.abspath('./data/gold.raw.txt')

GRAM_FILE = './data/erg.dat'
ACE_BIN = os.path.expanduser('~/bin/ace')
INPUT_TXT = 'data/speckled.txt'
INPUT_MRS = 'data/gold.out.txt'
OUTPUT_ISF = 'data/spec-isf.xml'
PRED_DEBUG_DUMP = 'data/speckled_synset_debug.txt'
GOLD_TAGS = 'data/speckled_tags_gold.txt'
SOURCE_CODE_DIR = os.path.dirname(os.path.realpath(__file__))
LICENSE_TEMPLATE_LOC = os.path.join(SOURCE_CODE_DIR, 'CCBY30_template.txt')
LICENSE_TEXT = open(LICENSE_TEMPLATE_LOC, 'r').read()

prettify_xml = lambda x: xml.dom.minidom.parseString(x).toprettyxml()

#-----------------------------------------------------------------------

class TSDBSentence:
    def __init__(self, sid, text, mrs=''):
        self.sid = sid
        self.ntuid = None
        self.text = text
        self.mrs = mrs

#-----------------------------------------------------------------------

def extract_tsdb_gold():
    t = Timer()

    t.start("Loading raw text from [%s] ..." % (RAW_TEXT,))
    raw_sentences = []
    with open(RAW_TEXT, 'r') as rawtext:
        lines = rawtext.readlines()
        for line in lines:
            parts = line.strip().split('\t')
            raw_sentences.append(TSDBSentence(parts[0], parts[1]))
    print("Number of raw sentences: %s" % len(raw_sentences))
    t.end("Raw text has been loaded.")
    
    t.start("Loading gold profile from: [%s] ..." % (GOLD_PROFILE,))
    prof = itsdb.ItsdbProfile(GOLD_PROFILE)

    # Read all items
    tbl_item = prof.read_table('item')
    gold_sentences = []
    sentences_map = dict()
    with open(GOLD_RAW, 'w') as gold_raw:
        for row in tbl_item:
            iid = row.get('i-id')
            raw_text = row.get('i-input').strip()
            sentences_map[iid] = TSDBSentence(iid, raw_text)
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

def read_data(file_path):
    data = []
    with open(file_path, 'r') as input_file:
        for line in input_file:
            data.append(tuple(line.split()))
    return data

def pred_to_key(pred):
    pred_obj = Pred.grammarpred(pred.label)
    return '-'.join((str(pred.cfrom), str(pred.cto), str(pred_obj.pos), str(pred_obj.lemma), str(pred_obj.sense)))

def read_ace_output(ace_output_file):
    print("Reading parsed MRS from %s..." % (ace_output_file,))
    c = Counter()
    items = []
    sentences = []
    skipped = []
    with open(ace_output_file, 'r') as input_mrs:
        current_sid = 0
        while True:
            current_sid += 1
            line = input_mrs.readline()
            if line.startswith('SENT'):
                mrs_line = input_mrs.readline()
                item = [line, mrs_line]
                s = Sentence(line[5:], sid=current_sid)
                sentences.append(s)
                while mrs_line.strip():
                    s.add(mrs_line)
                    mrs_line = input_mrs.readline()
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
    writelines(skipped, ace_output_file + '.skipped.txt')
    return sentences

def build_root_node():
    isf_node = ET.Element('rootisf')
    isf_node.set('version', '0.1')
    isf_node.set('lang', 'eng')
    # Add license information
    header_node = ET.SubElement(isf_node, 'headerisf')
    filedesc_node = ET.SubElement(header_node, 'description')
    filedesc_node.set("title", "The Adventure of the Speckled Band")
    filedesc_node.set("author", "Arthur Conan Doyle")
    filedesc_node.set("filename", "spec-isf.xml")
    filedesc_node.set("creationtime", datetime.datetime.now().isoformat())
    # License text
    license_node = ET.SubElement(filedesc_node, "license")
    license_node.text = LICENSE_TEXT
    # Processors
    procs_node = ET.SubElement(header_node, "linguisticProcessors")
    proc_node = ET.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "coolisf")
    proc_node.set("description", "Python implementation of Integrated Semantic Framework")
    proc_node.set("version", "pre 0.1")
    proc_node.set("url", "https://github.com/letuananh/intsem.fx")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    
    proc_node = ET.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "ACE")
    proc_node.set("description", "the Answer Constraint Engine (Delph-in)")
    proc_node.set("version", "0.9.17")
    proc_node.set("url", "http://moin.delph-in.net/AceTop")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    
    proc_node = ET.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "NLTK")
    proc_node.set("description", "Natural Language Toolkit for Python")
    proc_node.set("version", "3.0.4")
    proc_node.set("url", "http://www.nltk.org/")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    
    proc_node = ET.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "pyDelphin")
    proc_node.set("description", "Python libraries for DELPH-IN")
    proc_node.set("version", "0.3")
    proc_node.set("url", "https://github.com/delph-in/pydelphin")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    
    # Contributors
    contributors_node = ET.SubElement(header_node, "contributors")
    contributor_node = ET.SubElement(contributors_node, "contributor")
    contributor_node.set("name", "Le Tuan Anh")
    contributor_node.set("email", "tuananh.ke@gmail.com")
    contributor_node = ET.SubElement(contributors_node, "contributor")
    contributor_node.set("name", "Francis Bond")
    contributor_node.set("email", "fcbond@gmail.com")
    contributor_node = ET.SubElement(contributors_node, "contributor")
    contributor_node.set("name", "Dan Flickinger")
    contributor_node.set("email", "danf@stanford.edu")
    
    return isf_node

def generate_gold_profile():
    # Read human annotations from NTU-MC
    print("Reading gold annotations from NTU-MC")
    golddata = read_data(GOLD_TAGS)
    sid_gold_map = dd(list)
    for datum in golddata:
        sid_gold_map[datum[0]].append(datum)
    print("Gold map: %s" % [len(sid_gold_map)])
    
    # read_ace_output()
    # Read gold profile from ITSDB (ERG-TRUNK)
    sentences = []
    with open(INPUT_MRS) as input_mrs:
        lines = input_mrs.readlines()
        for line in lines:
            (ntuid, tsdbid, text, mrs) = line.split('\t')
            sent = Sentence(text=text, sid=int(ntuid))
            if mrs and len(mrs.strip()) > 0:
                sent.add(mrs)
                sent.raw_mrs.append(mrs)
            sentences.append(sent)
        
    # Process data
    print("Creating XML file ...")
    # build root XML node for data file
    isf_node = build_root_node()
    # Add document nodes
    doc_node = ET.SubElement(isf_node, 'document')
    doc_node.set('name', 'speckled band')
    preds_debug = []
    
    cgold = Counter()
    for sent in sentences:
        sid_key = str(sent.sid)
        goldtags = sid_gold_map[sid_key]
        sentence_to_xml(sent, doc_node, goldtags, preds_debug=preds_debug, cgold=cgold)
    print("Gold senses inserted")
    cgold.summarise()
    print("Dumping preds debug")
    writelines([ '\t'.join([str(i) for i in x]) for x in preds_debug], PRED_DEBUG_DUMP)
        #exit()
    with open(OUTPUT_ISF, 'w') as output_isf:
        print("Making it beautiful ...")
        xml_string = prettify_xml(ET.tostring(isf_node, encoding='utf-8'))
        print("Saving XML data to file ...")
        output_isf.write(xml_string)
    print("All done!")

def tag_dmrs_xml(mrs, dmrs_node, goldtags=None, sent_node=None, cgold=None):
    # WSD info
    best_candidate_map = {}
    for pred in mrs.preds():
        candidates = PredSense.search_pred_string(pred.label, False)
        if candidates:
            best_candidate_map[pred_to_key(pred)] = candidates[0]
    # inject sense tags into nodes
    for node in dmrs_node.findall('node'):
        # insert gold sense
        if goldtags:                    
            for tag in goldtags:
                if node.get('cfrom') and node.get('cto') and int(tag[1]) == int(node.get('cfrom')) and int(tag[2]) == int(node.get('cto')):
                    gold_node = ET.SubElement(node, 'sensegold')
                    gold_node.set('synset', tag[3])
                    gold_node.set('clemma', tag[4])
                    if cgold: cgold.count('inserted')
        realpred = node.find('realpred')
        if realpred is not None:
            # insert mcs
            key = '-'.join((str(node.get('cfrom')), str(node.get('cto')), str(realpred.get('pos')), str(realpred.get('lemma')), str(realpred.get('sense'))))
            if key in best_candidate_map:
                candidate = best_candidate_map[key]
                candidate_node = ET.SubElement(node, 'sense')
                candidate_node.set('pos', str(candidate.pos))
                candidate_node.set('synsetid', str(candidate.sid)[1:] + '-' + str(candidate.pos))  # [2015-10-26] FCB: synsetid format should be = 12345678-x]
                candidate_node.set('lemma', str(candidate.lemma))
                candidate_node.set('score', str(candidate.tagcount))

def sentence_to_xml(sent, doc_node=None, goldtags=None, preds_debug=None, cgold=None):
    if doc_node is not None:
        sent_node = ET.SubElement(doc_node, 'sentence')
    else:
        sent_node = ET.Element('sentence')
    sent_node.set('sid', str(sent.sid))
    text_node = ET.SubElement(sent_node, 'text')
    text_node.text = sent.text
    dmrses_node = ET.SubElement(sent_node, 'dmrses')
    if len(sent.mrs) == 0:
        return sent_node
    else:
        for mrs in sent.mrs:
            xml_string = mrs.dmrs_xml(False)
            dmrs_xml = ET.fromstring(xml_string)
            dmrses = dmrs_xml.findall('dmrs')
            for dmrs_node in dmrses:
                tag_dmrs_xml(mrs, dmrs_node, goldtags, cgold=cgold)
                dmrses_node.append(dmrs_node)
    return sent_node

#-----------------------------------------------------------------------

def main():
    print("Step 1: Extracting gold parse trees from Itsdb")
    extract_tsdb_gold()
    
    print("Step 2: Generating gold profile as XML")
    generate_gold_profile()

if __name__ == "__main__":
    main()
