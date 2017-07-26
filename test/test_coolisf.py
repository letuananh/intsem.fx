#!/Usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script for testing coolisf library
Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
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
__copyright__ = "Copyright 2015, pyisf"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import unittest
import logging

from lelesk import LeLeskWSD, LeskCache

from coolisf.gold_extract import export_to_visko
from coolisf.util import read_ace_output
from coolisf.model import Sentence, DMRS
from coolisf.util import GrammarHub
from yawlib import YLConfig, WordnetSQL as WSQL


########################################################################

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Change this to DEBUG for more information

wsql = WSQL(YLConfig.WNSQL30_PATH)
TEST_DIR = os.path.dirname(__file__)
TEST_DATA = os.path.join(TEST_DIR, 'data')
TEST_SENTENCES = 'data/bib.txt'
ACE_OUTPUT_FILE = 'data/bib.mrs.txt'


class TestGrammarHub(unittest.TestCase):

    ghub = GrammarHub()

    def test_all_grammars(self):
        for n in ('JACY', 'VRG', 'ERG'):
            self.assertIn(n, self.ghub.names)

    def test_grammar_names(self):
        gm = self.ghub.available
        self.assertEqual(gm['JACYMC'], 'JACY/MeCab')

    def test_config(self):
        erg = self.ghub.ERG
        self.assertIsNotNone(erg)

    def test_parse_cache(self):
        txt = "I saw a girl with a telescope."
        self.ghub.ERG.parse(txt, 5)
        s = self.ghub.ERG.cache.load(txt, self.ghub.ERG.name, 5)
        self.assertIsNotNone(s)
        self.assertEqual(len(s), 5)

    def test_isf_cache(self):
        txt = "I saw a girl with a telescope."
        grm = "ERG"
        pc = 5
        tagger = "MFS"
        s = self.ghub.parse(txt, grm, pc, tagger)
        s = self.ghub.cache.load(txt, grm, pc, tagger)
        self.assertIsNotNone(s)
        self.assertEqual(len(s['parses']), 5)


class TestMain(unittest.TestCase):

    ghub = GrammarHub()
    ERG = ghub.ERG

    def test_models(self):
        raw_text = 'It rains.'
        raw_mrs = '''[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]'''
        sent = Sentence(raw_text, 1)
        sent.add(raw_mrs)
        self.assertEqual(sent.text, raw_text)
        self.assertEqual(len(sent), 1)
        self.assertIsNotNone(sent[0].mrs())
        self.assertIsNotNone(sent[0].dmrs())
        self.assertIsNotNone(sent[0].dmrs().to_mrs())
        self.assertIsNotNone(sent[0].mrs().to_dmrs())

    def test_ace_output_to_xml(self):
        sentences = read_ace_output(ACE_OUTPUT_FILE)
        self.assertIsNotNone(sentences)

        sent = sentences[0]
        self.assertGreaterEqual(len(sent), 3)
        # sentence to XML
        xml = sent.to_xml_node()
        self.assertIsNotNone(xml)
        # ensure DMRS nodes count
        dmrs_nodes = xml.findall('./dmrses/dmrs')
        self.assertGreaterEqual(len(dmrs_nodes), 3)

    def test_txt_to_dmrs(self):
        print("Test parsing raw text sentences")
        with open(TEST_SENTENCES) as test_file:
            raw_sentences = test_file.readlines()
            sentences = [self.ERG.parse(x, 5) for x in raw_sentences]
            self.assertEqual(len(sentences[0]), 5)
            self.assertEqual(len(sentences[1]), 5)
            self.assertEqual(len(sentences[2]), 0)
            p0 = sentences[0][0]
            self.assertIsNotNone(p0.dmrs().xml())
            print("Test sense tag")
            xnode = p0.dmrs().tag_xml()
            senses = xnode.findall('./node/sense')
            self.assertGreater(len(senses), 0)

    def test_sensetag_in_json(self):
        text = "Some dogs chases a cat."
        a_sent = self.ERG.parse(text)
        p = a_sent[0]
        # check json
        self.assertEqual(type(p.dmrs().json()), dict)
        self.assertEqual(type(p.dmrs().json_str()), str)
        # check sense tagging
        tags = p.dmrs().tag()
        j = p.dmrs().json()
        nodes = j['nodes']
        self.assertEqual(len(nodes), 8)
        self.assertEqual(len(tags), 4)
        self.assertEqual(len(nodes[2]['senses']), 1)
        self.assertEqual(len(nodes[4]['senses']), 1)
        self.assertEqual(len(nodes[5]['senses']), 1)
        self.assertEqual(len(nodes[7]['senses']), 1)
        self.assertEqual(nodes[0]['type'], 'realpred')
        self.assertEqual(nodes[1]['type'], 'gpred')
        self.assertEqual(nodes[0]['pos'], 'q')
        self.assertEqual(nodes[7]['pos'], 'n')
        logging.debug("Tagged JSON (with MFS): {}".format(p.dmrs().json_str()))

    def test_mrs_formats(self):
        text = "Some dogs chase some cats."
        a_sent = self.ERG.parse(text)
        p = a_sent[0]
        # Create sentence object from raw data
        sent = Sentence(a_sent.text)
        sent.add(p.mrs().tostring())
        self.assertIsNotNone(sent)
        p2 = sent[0]
        self.assertEqual(len(sent), 1)
        self.assertEqual(str(p2.mrs().tostring())[:20], '[ TOP: h0\n  INDEX: e')
        # now make DMRS XML ...
        xml_str = p2.dmrs().xml_str()
        self.assertTrue(xml_str.startswith('<dmrs cfrom="'))
        # add new DMRS from XML
        sent.add(dmrs_xml=xml_str)
        self.assertEqual(len(sent), 2)  # now we should have 2 MRSes
        m2 = sent[1]
        # and they should look exactly the same
        xml_str2 = m2.dmrs().xml_str()
        self.assertEqual(xml_str, xml_str2)
        pass

    def test_lelesk_integration(self):
        text = "A big bird is flying on the sky."
        a_sent = self.ERG.parse(text)
        context = [p.pred.lemma for p in a_sent[0].dmrs().obj().eps()]
        preds = a_sent[0].dmrs().obj().eps()
        wsd = LeLeskWSD(dbcache=LeskCache())
        for w, p in zip(context, preds):
            scores = wsd.lelesk_wsd(w, '', lemmatizing=False, context=context)
            if scores:
                logger.debug("Word: {w} (p={p}|{nid}) => {ss} | Score: {sc} | Def: {d}".format(w=w, p=str(p.pred), nid=p.nodeid, ss=scores[0].candidate.synset, sc=scores[0].score, d=scores[0].candidate.synset.glosses[0].text()))
            else:
                logger.debug("Word: {w} => N/A".format(w=w))

    def test_sensetag_using_lelesk(self):
        text = "A big bird is flying on the sky."
        logging.info("Tagging ``{s}'' using lelesk".format(s=text))
        a_sent = self.ERG.parse(text)
        d = a_sent[0].dmrs()
        d.tag(method='lelesk')
        self.assertTrue(d.tags)
        js = d.json_str()
        logger.debug("Tagged JSON (using LeLesk): {}".format(js))

    def test_parse_no(self):
        text = "I saw a girl with a big telescope which is nice."
        a_sent = self.ERG.parse(text)
        self.assertEqual(len(a_sent), 5)  # default is 5
        # increase parse count to 7
        a_sent = self.ERG.parse(text, parse_count=7)
        self.assertEqual(len(a_sent), 7)
        # increase parse count to 10
        a_sent = self.ERG.parse(text, parse_count=10)
        self.assertEqual(len(a_sent), 10)

    def test_fix_tokenization(self):
        text = 'It rains.'
        sent = self.ERG.parse(text)
        # to visko
        d = sent[0].dmrs()
        logger.debug("JSON obj: {}", d.json())
        logger.debug("All tags: {}", d.tags)
        ep = d.obj().ep(10000)
        print(d.fix_tokenization(ep, text))

    def text_isf_visko(self):
        sents = read_gold_sentences(auto_tag=False)
        s10044 = sents[44]
        p = s10044[0]
        # test convert back and forth
        print(p.mrs().to_dmrs().to_mrs().obj())
        # test export to visko (XML)
        from chirptext.leutile import FileTool
        FileTool.create_dir(TEST_DATA)
        export_to_visko([s10044], TEST_DATA)
        # test re-read that visko XML
        x = s10044.to_visko_xml_str()
        d = DMRS(x)
        self.assertIsNotNone(d.obj())
        # Test read back from XML file
        f = os.path.join(TEST_DATA, 'v10044.xml')
        print(f)
        with open(f, 'r') as infile:
            print("Read back from file")
            x = infile.read()
            print(len(x))
            d = DMRS(x)
            print(d.obj())

    def test_preserve_xml_tag_in_json(self):
        sent = self.ERG.parse('I like hot dog.')
        goldtags = ((-1, 11, 15, '12345678-n', 'uberdog', 'NN'),)
        sent.tag(goldtags, method='mfs')
        d = sent[0].dmrs()
        # now tag this manually
        from chirptext.texttaglib import TagInfo
        self.assertIsNotNone(d.json_str())
        self.assertEqual(len(d.tags), 3)
        self.assertEqual(len(d.tags[10006]), 2)
        ss, method = d.tags[10006][0]
        self.assertEqual(method, TagInfo.GOLD)
        self.assertEqual(ss.synsetid, '12345678-n')
        logger.debug("JSON str: {}".format(d.json_str()))


########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
