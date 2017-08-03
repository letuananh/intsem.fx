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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import sys
import datetime
import argparse
from collections import defaultdict as dd
import gzip
from lxml import etree

from delphin import itsdb

from fuzzywuzzy import fuzz

from chirptext.leutile import FileHelper
from chirptext.leutile import Timer
from chirptext.leutile import StringTool
from chirptext.leutile import Counter
from chirptext.texttaglib import TaggedDoc, TagInfo

from yawlib.models import SynsetID
from coolisf.model import Sentence
from coolisf.util import read_ace_output

from .lexsem import tag_gold

##########################################
# CONFIGURATION
##########################################

DATA_DIR = FileHelper.abspath('./data')
GOLD_PROFILE = os.path.join(DATA_DIR, 'gold')
GOLD_MRS_FILE = 'data/gold.out.txt'
tagdoc = TaggedDoc(DATA_DIR, 'gold')
OUTPUT_ISF = 'data/spec-isf.xml'

MY_DIR = os.path.dirname(os.path.realpath(__file__))
LICENSE_TEMPLATE_LOC = os.path.join(MY_DIR, 'CCBY30_template.txt')
LICENSE_TEXT = open(LICENSE_TEMPLATE_LOC, 'r').read()


#-----------------------------------------------------------------------

class TSDBSentence:
    def __init__(self, sid, text, mrs=''):
        self.sid = sid
        self.ntuid = None
        self.text = text
        self.mrs = mrs


#-----------------------------------------------------------------------

def extract_tsdb_gold():
    # read NTU-MC
    raw_sentences = []
    tagdoc.read()
    for s in tagdoc:
        raw_sentences.append(TSDBSentence(s.ID, s.text))
    # read Itsdb
    prof = itsdb.ItsdbProfile(GOLD_PROFILE)

    # Read all items
    tbl_item = prof.read_table('item')
    gold_sentences = []
    sentences_map = dict()
    for row in tbl_item:
        iid = row.get('i-id')
        raw_text = row.get('i-input').strip()
        sentences_map[iid] = TSDBSentence(iid, raw_text)
        gold_sentences.append(sentences_map[iid])

    # Read all parse results
    tbl_result = prof.read_table('result')
    for row in tbl_result:
        pid = row.get('parse-id')
        mrs = row.get('mrs')
        if pid not in sentences_map:
            print('pid %s cannot be found' % pid)
        else:
            sentences_map[pid].mrs = StringTool.to_str(mrs)

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
    with open(GOLD_MRS_FILE, 'w') as outfile:
        for sent in gold_sentences:
            outfile.write('%s\t%s\t%s\t%s\n' % (sent.ntuid, sent.sid, sent.text, sent.mrs))

    # Verification
    with open(GOLD_MRS_FILE, 'r') as testfile:
        for line in testfile:
            parts = line.split('\t')
            if len(parts) != 4:
                print("WARNING: INVALID LINE")
    print("All done!")


def read_data(file_path):
    data = []
    with open(file_path, 'r') as input_file:
        for line in input_file:
            data.append(tuple(line.split()))
    return data


def build_root_node():
    isf_node = etree.Element('rootisf')
    isf_node.set('version', '0.1')
    isf_node.set('lang', 'eng')
    # Add license information
    header_node = etree.SubElement(isf_node, 'headerisf')
    filedesc_node = etree.SubElement(header_node, 'description')
    filedesc_node.set("title", "The Adventure of the Speckled Band")
    filedesc_node.set("author", "Arthur Conan Doyle")
    filedesc_node.set("filename", "spec-isf.xml")
    filedesc_node.set("creationtime", datetime.datetime.now().isoformat())
    # License text
    license_node = etree.SubElement(filedesc_node, "license")
    license_node.text = LICENSE_TEXT
    # CoolISF
    procs_node = etree.SubElement(header_node, "linguisticProcessors")
    proc_node = etree.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "coolisf")
    proc_node.set("description", "Python implementation of Integrated Semantic Framework")
    proc_node.set("version", "pre 0.1")
    proc_node.set("url", "https://github.com/letuananh/intsem.fx")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    # ACE
    proc_node = etree.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "ACE")
    proc_node.set("description", "the Answer Constraint Engine (Delph-in)")
    proc_node.set("version", "0.9.17")
    proc_node.set("url", "http://moin.delph-in.net/AceTop")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    # NLTK
    proc_node = etree.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "NLTK")
    proc_node.set("description", "Natural Language Toolkit for Python")
    proc_node.set("version", "3.0.4")
    proc_node.set("url", "http://www.nltk.org/")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    # pyDelphin
    proc_node = etree.SubElement(procs_node, "linguisticProcessor")
    proc_node.set("name", "pyDelphin")
    proc_node.set("description", "Python libraries for DELPH-IN")
    proc_node.set("version", "0.3")
    proc_node.set("url", "https://github.com/delph-in/pydelphin")
    proc_node.set("timestamp", datetime.datetime.now().isoformat())
    # Contributors
    contributors_node = etree.SubElement(header_node, "contributors")
    contributor_node = etree.SubElement(contributors_node, "contributor")
    contributor_node.set("name", "Le Tuan Anh")
    contributor_node.set("email", "tuananh.ke@gmail.com")
    contributor_node = etree.SubElement(contributors_node, "contributor")
    contributor_node.set("name", "Francis Bond")
    contributor_node.set("email", "fcbond@gmail.com")
    contributor_node = etree.SubElement(contributors_node, "contributor")
    contributor_node.set("name", "Dan Flickinger")
    contributor_node.set("email", "danf@stanford.edu")
    return isf_node


def read_gold_mrs():
    # Read gold profile from ITSDB (ERG-TRUNK)
    sentences = []
    # Generate INPUT_MRS file (gold.out.txt) if needed
    if not os.path.isfile(GOLD_MRS_FILE):
        extract_tsdb_gold()
    with open(GOLD_MRS_FILE) as input_mrs:
        lines = input_mrs.readlines()
        for line in lines:
            (ntuid, tsdbid, text, mrs) = line.split('\t')
            sent = Sentence(text=text, sid=int(ntuid))
            if mrs and len(mrs.strip()) > 0:
                sent.add(mrs_str=mrs)
            sentences.append(sent)
    return sentences


def read_gold_sents():
    tagdoc.read()
    filter_wrong_senses(tagdoc)
    sentences = read_gold_mrs()
    # sense tagging
    for sent in sentences:
        if len(sent) == 0:
            print("WARNING: empty sentence #{}: {}".format(sent.sid, sent.text))
            continue
        dmrs = sent[0].dmrs()
        tagged = tagdoc.sent_map[str(sent.sid)]
        tag_gold(dmrs, tagged, sent.text)
        sent.tag(method=TagInfo.MFS)
        sent.tag_xml()
    return sentences


def generate_gold_profile():
    sentences = read_gold_sents()
    # Process data
    print("Creating XML file ...")
    # build root XML node for data file
    isf_node = build_root_node()
    # Add document nodes
    doc_node = etree.SubElement(isf_node, 'document')
    doc_node.set('name', 'speckled band')
    # export to XML
    for sent in sentences:
        sent.to_xml_node(doc_node)
    # write to file
    with open(OUTPUT_ISF, 'wb') as output_isf:
        print("Making it beautiful ...")
        xml_string = etree.tostring(isf_node, encoding='utf-8', pretty_print=True)
        print("Saving XML data to file ...")
        output_isf.write(xml_string)
    print("ISF gold profile has been written to %s" % (OUTPUT_ISF,))
    print("All done!")


GOLD_WRONG = {
    '02108026-v': [10109, 10114, 10178, 10593],  # => {'have'}
    '00066781-r': [10405, 10498, 10501],  # => {'in front'}
    '01554230-a': [10468, 10582],  # => {'such'}
    '01712704-v': [10061, 10265, 10358, 10384],  # => {'do'}
    '01188342-v': [10292],  # => {'be full'}
}


def filter_wrong_senses(doc):
    for sent in doc:
        to_remove = []
        for c in sent.concepts:
            if c.tag[0] in '=!':
                c.tag = c.tag[1:]
            if c.tag in GOLD_WRONG and int(sent.ID) in GOLD_WRONG[c.tag]:
                to_remove.append(c)
        for c in to_remove:
            sent.concept_map.pop(c.cid)


def export_to_visko(sents, doc_path, pretty_print=True):
    if not os.path.exists(doc_path):
        os.makedirs(doc_path)
    print("Exporting %s sentences to Visko" % (len(sents),))
    print("Visko doc path: {}".format(doc_path))
    for sent in sents:
        sentpath = os.path.join(doc_path, str(sent.sid) + '.xml.gz')
        with gzip.open(sentpath, 'w') as f:
            f.write(etree.tostring(sent.to_visko_xml(), encoding='utf-8', pretty_print=pretty_print))
    print("Done!")


#-----------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="ISF Gold Extractor")

    parser.add_argument('-g', '--gold', help='Extract gold profile', action='store_true')
    parser.add_argument('--visko', help='Export to VISKO', action='store_true')
    parser.add_argument('-d', '--dev', help='Dev mode', action='store_true')
    parser.add_argument('-x', '--extract', help='Extract TSDB gold', action='store_true')

    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        if args.extract:
            extract_tsdb_gold()
        elif args.visko:
            sents = read_ace_output('data/wndefs.nokey.mrs.txt')
            export_to_visko(sents[:200], os.path.expanduser('~/wk/vk/data/biblioteche/test/wn/wndef/'))
        elif args.gold:
            # print("Step 2: Generating gold profile as XML")
            generate_gold_profile()
        else:
            parser.print_help()
    pass


if __name__ == "__main__":
    main()
