# -*- coding: utf-8 -*-

"""
Generate gold profile
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import datetime
import gzip
import logging
from lxml import etree


from texttaglib.chirptext.leutile import FileHelper
from texttaglib.chirptext import texttaglib as ttl
from texttaglib.chirptext import chio
from lelesk import LeLeskWSD
from lelesk import LeskCache  # WSDResources

from coolisf.data import read_ccby30
from coolisf.dao import read_tsdb
from coolisf.model import Sentence
from coolisf.lexsem import tag_gold, Lexsem
from coolisf.mappings import PredSense
from coolisf.common import write_file
from coolisf.config import read_config


# -----------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------

cfg = read_config()
if cfg and 'data_root' in cfg:
    DATA_DIR = FileHelper.abspath(cfg['data_root'])
else:
    DATA_DIR = FileHelper.abspath('./data')
GOLD_PATH = os.path.join(DATA_DIR, 'gold', 'gold_erg')
GOLD_TTL_PATH = os.path.join(DATA_DIR, 'gold', 'gold_imi')
OUTPUT_ISF = os.path.join(DATA_DIR, 'gold', 'speckled_tsdb_imi.xml.gz')


def getLogger():
    return logging.getLogger(__name__)


# -----------------------------------------------------------------------

def match_sents(isf_doc, ttl_doc):
    """ Match TSDB profile sentences with TTL sentences """
    if len(isf_doc) != len(ttl_doc):
        getLogger().info("ISF doc size: {}".format(len(isf_doc)))
        getLogger().info("TTL doc size: {}".format(len(ttl_doc)))
        for sent in isf_doc:
            if not ttl_doc.get(sent.ident, default=None):
                getLogger().warning("Sentence ID(s) in ISF doc and TTL doc are different.")
                return None
        # it's possible to match all
        for sent in isf_doc:
            sent.shallow = ttl_doc.get(sent.ident)
        return isf_doc
    # else
    for isf_sent, ttl_sent in zip(isf_doc, ttl_doc):
        if isf_sent.text != ttl_sent.text:
            # try to match all available sentences
            getLogger().warning("Sentence(s) in ISF doc and TTL doc are different. E.g. ISF/#{}: {} vs TTL/#{}: {}".format(isf_sent.ident, isf_sent.text, ttl_sent.ID, ttl_sent.text))
            return None
    # only import when everything could be matched
    for isf_sent, ttl_sent in zip(isf_doc, ttl_doc):
        isf_sent.shallow = ttl_sent
    return isf_doc


def tag_doc(isf_doc, ttl_doc, use_ttl_sid=True, wsd_method=None, wsd=None, taggold=True, on_error='raise', ctx=None, **kwargs):
    """ Tag an ISF document using a TTL """
    isf_doc = match_sents(isf_doc, ttl_doc)
    if isf_doc is None:
        raise Exception("isf_doc and ttl_doc could not be matched")
    not_matched = set()
    wsd = LeLeskWSD(dbcache=LeskCache())
    ctx = PredSense.wn.ctx()
    to_remove = set()
    for sent in isf_doc:
        if use_ttl_sid and sent.shallow and sent.shallow.ID:
            sent.ident = sent.shallow.ID
        for reading in sent:
            if wsd_method:
                sent.tag(method=wsd_method, wsd=wsd, ctx=ctx)
            if taggold and sent.shallow:
                try:
                    m, n, ignored = tag_gold(reading.dmrs(), sent.shallow, sent.text, **kwargs)
                except:
                    getLogger().exception("Could not process sentence #{}: {}".format(sent.ident, sent.text))
                    if on_error == 'ignore':
                        continue
                    elif on_error == 'remove':
                        to_remove.add(sent)
                        break
                    else:
                        raise
                # getLogger().debug("Matched: {}".format(m))
                if n:
                    not_matched.add(sent.ident)
                    sent.flag = Sentence.ERROR
            # update XML
            reading.dmrs().tag_xml(method=None, update_back=True, wsd=wsd, ctx=ctx)
        sent.tag_xml()
    for sent in to_remove:
        isf_doc.remove(sent)
    if not_matched:
        getLogger().warning("TSDB/IMI mismatched sentences: {} - IDs={}".format(len(not_matched), not_matched))
    return isf_doc


def read_tsdb_ttl(tsdb_path, ttl_path=None, name=None, title=None, *args, **kwargs):
    """ Combine TSDB profile and TTL profile to create ISF document (shallow + deep)
    This function return an instance of coolisf.model.Document
    """
    tsdb_doc = read_tsdb(tsdb_path, name=name, title=title)
    if ttl_path is None:
        ttl_path = tsdb_path
    ttl_doc = ttl.Document.read_ttl(ttl_path)
    isf_doc = tag_doc(tsdb_doc, ttl_doc, *args, **kwargs)
    getLogger().debug("TTL doc {} contains {} sentence(s).".format(ttl_path, len(ttl_doc)))
    getLogger().debug("isf_doc size: {}".format(len(isf_doc)))
    return isf_doc


def read_gold_mrs():
    """ Read gold MRS only (without TTL) """
    return read_tsdb(GOLD_PATH, name="speckled", title="The Adventure of the Speckled Band")


def read_gold_sents(perform_wsd=False):
    """ Read gold sentences (TSDB+TTL) """
    return read_tsdb_ttl(GOLD_PATH, name="speckled", title="The Adventure of the Speckled Band")


def build_root_node(filename='spec-isf.xml'):
    isf_node = etree.Element('rootisf')
    isf_node.set('version', '0.1')
    isf_node.set('lang', 'eng')
    # Add license information
    header_node = etree.SubElement(isf_node, 'headerisf')
    filedesc_node = etree.SubElement(header_node, 'description')
    filedesc_node.set("title", "The Adventure of the Speckled Band")
    filedesc_node.set("author", "Arthur Conan Doyle")
    filedesc_node.set("filename", filename)
    filedesc_node.set("creationtime", datetime.datetime.now().isoformat())
    # License text
    license_node = etree.SubElement(filedesc_node, "license")
    license_node.text = etree.CDATA(read_ccby30())
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
    doc = read_tsdb_ttl(GOLD_PATH, ttl_path=GOLD_TTL_PATH)
    # Process data
    print("Creating XML file ...")
    # build root XML node for data file
    isf_node = build_root_node(filename=FileHelper.getfullfilename(OUTPUT_ISF))
    # Add document nodes
    doc.to_xml_node(isf_node)
    # write to file
    print("Making it beautiful ...")
    xml_string = etree.tostring(isf_node, encoding='utf-8', pretty_print=True)
    print("Saving XML data to file ...")
    write_file(xml_string, OUTPUT_ISF)
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
            getLogger().debug("popping {} in sent #{}".format(repr(c.cidx), sent.ID))
            sent.pop_concept(c.cidx)


def export_to_visko(sents, doc_path, pretty_print=True, separate=True, halt_on_error=True):
    """ Export sentences to XML files """
    print("Exporting %s sentences to Visko" % (len(sents),))
    print("Visko doc path: {}".format(doc_path))
    if separate:
        if not os.path.exists(doc_path):
            os.makedirs(doc_path)
        for sent in sents:
            sentpath = os.path.join(doc_path, str(sent.ident) + '.xml.gz')
            with gzip.open(sentpath, 'w') as f:
                try:
                    f.write(etree.tostring(sent.to_xml_node(), encoding='utf-8', pretty_print=pretty_print))
                except:
                    print("ERROR")
    else:
        # write to file
        chio.write_file(doc_path, sents.to_xml_str(pretty_print=pretty_print, strict=halt_on_error))
    print("Done!")
