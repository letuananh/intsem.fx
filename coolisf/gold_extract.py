# -*- coding: utf-8 -*-

'''
Generate gold profile
Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    argparse module:
        https://docs.python.org/3/howto/argparse.html
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
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

########################################################################

import os
import datetime
import gzip
import logging
from lxml import etree


from chirptext.leutile import FileHelper
from chirptext import texttaglib as ttl

from coolisf.dao import read_tsdb
from coolisf.model import Sentence
from coolisf.lexsem import tag_gold


# -----------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------

DATA_DIR = FileHelper.abspath('./data')
GOLD_PATH = os.path.join(DATA_DIR, 'gold')
OUTPUT_ISF = 'data/spec-isf.xml'

MY_DIR = os.path.dirname(os.path.realpath(__file__))
LICENSE_TEMPLATE_LOC = os.path.join(MY_DIR, 'CCBY30_template.txt')
LICENSE_TEXT = open(LICENSE_TEMPLATE_LOC, 'r').read()


def getLogger():
    return logging.getLogger(__name__)


# -----------------------------------------------------------------------

def match_sents(isf_doc, ttl_doc):
    ''' Match TSDB profile sentences with TTL sentences '''
    for isf_sent, ttl_sent in zip(isf_doc, ttl_doc):
        if isf_sent.text != ttl_sent.text:
            return None
    # only import when everything could be matched
    for isf_sent, ttl_sent in zip(isf_doc, ttl_doc):
        isf_sent.shallow = ttl_sent
    return isf_doc


def read_tsdb_ttl(tsdb_path, ttl_path=None, name=None, title=None, wsd_method=None, use_ttl_sid=True):
    ''' Combine TSDB profile and TTL profile to create ISF document (shallow + deep)
    This function return an instance of coolisf.model.Document
    '''
    tsdb_doc = read_tsdb(tsdb_path, name=name, title=title)
    if ttl_path is None:
        ttl_path = tsdb_path
    ttl_doc = ttl.Document.read_ttl(ttl_path)
    isf_doc = match_sents(tsdb_doc, ttl_doc)
    getLogger().debug("TTL doc {} contains {} sentence(s).".format(ttl_path, len(ttl_doc)))
    getLogger().debug("isf_doc size: {}".format(len(isf_doc)))
    not_matched = []
    for sent in isf_doc:
        if use_ttl_sid and sent.shallow and sent.shallow.ID:
            sent.ident = sent.shallow.ID
        for reading in sent:
            if wsd_method:
                sent.tag(method=wsd_method)
            if sent.shallow:
                m, n = tag_gold(reading.dmrs(), sent.shallow, sent.text)
                # getLogger().debug("Matched: {}".format(m))
                if n:
                    not_matched.append(sent.ident)
                    sent.flag = Sentence.ERROR
            # update XML
            reading.dmrs().tag_xml(method=None, update_back=True)
        sent.tag_xml()
    if not_matched:
        getLogger().warning("Not matched sentences: {}".format(not_matched))
    return isf_doc


def read_gold_mrs():
    ''' Read gold MRS only (without TTL) '''
    return read_tsdb(GOLD_PATH, name="speckled", title="The Adventure of the Speckled Band")


def read_gold_sents(perform_wsd=False):
    ''' Read gold sentences (TSDB+TTL) '''
    return read_tsdb_ttl(GOLD_PATH, name="speckled", title="The Adventure of the Speckled Band")


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
    license_node.text = etree.CDATA(LICENSE_TEXT)
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


def generate_gold_profile():
    # doc = read_gold_sents()
    print("Reading TSDB/TTL data")
    doc = read_tsdb_ttl(GOLD_PATH)
    # Process data
    print("Creating XML file ...")
    # build root XML node for data file
    isf_node = build_root_node()
    # Add document nodes
    doc.to_xml_node(isf_node)
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
            sent.pop_concept(c.ID)


def export_to_visko(sents, doc_path, pretty_print=True):
    if not os.path.exists(doc_path):
        os.makedirs(doc_path)
    print("Exporting %s sentences to Visko" % (len(sents),))
    print("Visko doc path: {}".format(doc_path))
    for sent in sents:
        sentpath = os.path.join(doc_path, str(sent.ident) + '.xml.gz')
        with gzip.open(sentpath, 'w') as f:
            f.write(etree.tostring(sent.to_xml_node(), encoding='utf-8', pretty_print=pretty_print))
    print("Done!")
