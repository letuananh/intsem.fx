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

from chirptext import FileHelper
from chirptext.texttaglib import TagInfo
from lelesk import LeLeskWSD, LeskCache

from coolisf.gold_extract import export_to_visko, read_gold_mrs
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
        s = self.ghub.parse_json(txt, grm, pc, tagger)
        # print(self.ghub.cache.ds.path)
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
        self.assertGreaterEqual(len(nodes), 8)
        self.assertEqual(len(tags), 4)
        for node in nodes:
            nid = node['nodeid']
            if nid in (10004, 10005, 10006, 10008):
                self.assertEqual(len(node['senses']), 1)
            if nid == 10001:
                self.assertEqual(node['type'], 'realpred')
            if nid == 10002:
                self.assertEqual(node['type'], 'gpred')
            if nid == 10008:
                self.assertEqual(node['pos'], 'n')

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
        # print(js)

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

    def test_generation(self):
        text = 'I did it.'
        sent = self.ERG.parse(text)
        g_sents = self.ERG.generate(sent[0])
        texts = [g.text for g in g_sents]
        self.assertIn('I did it.', texts)
        self.assertIn('It was done by me.', texts)

    def test_generation_jp(self):
        text = '雨が降る。'
        JACYDK = self.ghub.JACYDK
        sent = JACYDK.parse(text)
        g_sents = JACYDK.generate(sent[0])
        texts = [g.text for g in g_sents]
        self.assertIn('雨 が 降る', texts)

    def test_mrs_xml(self):
        mrs = '''[ TOP: h0
  RELS: < [ def_explicit_q_rel<0:3> LBL: h1 ARG0: x12 [ x NUM: sg IND: + PERS: 3 ] RSTR: h17 ]
          [ poss_rel<0:3> LBL: h2 ARG0: e10 [ e MOOD: indicative PERF: - SF: prop PROG: - TENSE: untensed ] ARG1: x12 ARG2: x11 [ x NUM: sg PT: std PERS: 1 ] ]
          [ pronoun_q_rel<0:3> LBL: h3 ARG0: x11 RSTR: h18 ]
          [ pron_rel<0:3> LBL: h4 ARG0: x11 ]
          [ _name_n_of_rel<4:8> LBL: h2 ARG0: x12 ]
          [ _be_v_id_rel<9:11> LBL: h5 ARG0: e13 [ e MOOD: indicative PERF: - SF: prop PROG: - TENSE: pres ] ARG1: x12 ARG2: x16 [ x NUM: sg IND: + PERS: 3 ] ]
          [ proper_q_rel<12:28> LBL: h6 ARG0: x16 RSTR: h19 ]
          [ compound_rel<12:28> LBL: h7 ARG0: e14 [ e MOOD: indicative PERF: - SF: prop PROG: - TENSE: untensed ] ARG1: x16 ARG2: x15 [ x NUM: sg PT: notpro IND: + PERS: 3 ] ]
          [ proper_q_rel<12:20> LBL: h8 ARG0: x15 RSTR: h20 ]
          [ named_rel<12:20> LBL: h9 ARG0: x15 CARG: "Sherlock" ]
          [ named_rel<21:28> LBL: h7 ARG0: x16 CARG: "Holmes" ] >
  HCONS: < h0 qeq h5 h17 qeq h2 h18 qeq h4 h19 qeq h7 h20 qeq h9 > ]
'''
        sent = Sentence()
        sent.add(mrs)
        # print(sent.to_xml_str())
        sent.add(dmrs_xml=sent[0].dmrs().xml_str())
        # print(sent[1])

    def text_isf_visko(self):
        sents = read_gold_mrs()
        s10044 = sents[44]
        p = s10044[0]
        # test convert back and forth
        print(p.mrs().to_dmrs().to_mrs().obj())
        # test export to visko (XML)
        FileHelper.create_dir(TEST_DATA)
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
            # print(d.obj())

    def test_preserve_xml_tag_in_json(self):
        sent = self.ERG.parse('I like hot dog.')
        sent.tag(TagInfo.MFS)
        d = sent[0].dmrs()
        self.assertIsNotNone(d.json_str())
        self.assertEqual(len(d.tags), 3)
        self.assertEqual(len(d.tags[10006]), 1)
        ss, method = d.tags[10006][0]
        logger.debug("JSON str: {}".format(d.json_str()))

    def test_preserve_shallow(self):
        txt = "雨が降る。"
        sent = self.ghub.parse_json(txt, "JACYDK")
        # load cached
        cached = self.ghub.cache.load(txt, "JACYDK", None, None)
        self.assertEqual(cached["shallow"], sent["shallow"])


########################################################################

if __name__ == "__main__":
    unittest.main()
