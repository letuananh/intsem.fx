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

import unittest
from lxml import etree

from lelesk import LeLeskWSD, LeskCache

from coolisf.util import read_ace_output
from coolisf.model import Sentence
from coolisf.util import Grammar

########################################################################

TEST_SENTENCES = 'data/bib.txt'
ACE_OUTPUT_FILE = 'data/bib.mrs.txt'


class TestMain(unittest.TestCase):

    ERG = Grammar()

    def test_ace_output_to_xml(self):
        sentences = read_ace_output(ACE_OUTPUT_FILE)
        self.assertIsNotNone(sentences)

        sent = sentences[0]
        self.assertEqual(len(sent.mrses), 3)
        # sentence to XML
        xml = sent.to_xml_node()
        self.assertIsNotNone(xml)
        # ensure DMRS nodes count
        dmrs_nodes = xml.findall('./dmrses/dmrs')
        self.assertEqual(len(dmrs_nodes), 3)

    def test_txt_to_dmrs(self):
        print("Test parsing raw text sentences")
        with open(TEST_SENTENCES) as test_file:
            raw_sentences = test_file.readlines()
            sentences = [self.ERG.txt2dmrs(x) for x in raw_sentences]
            self.assertEqual(len(sentences[0].mrses), 5)
            self.assertEqual(len(sentences[1].mrses), 5)
            self.assertEqual(len(sentences[2].mrses), 0)
            mrs0 = sentences[0].mrses[0]
            self.assertIsNotNone(mrs0.dmrs_xml(pretty_print=True))
            print("Test sense tag")
            xmlstr = sentences[0].to_xml_str(pretty_print=True)
            with open('data/temp.xml', 'w') as outfile:
                outfile.write(xmlstr)
            tagged = xmlstr.count('<sense')
            self.assertGreater(tagged, 0)

    def test_sensetag_in_json(self):
        text = "Some dogs chases a cat."
        a_sent = self.ERG.txt2dmrs(text)
        dmrs = a_sent.mrses[0]
        # check json
        self.assertEqual(type(dmrs.dmrs_json()), dict)
        self.assertEqual(type(dmrs.dmrs_json_str()), str)
        # check sense tagging
        tags = dmrs.tag()
        j = dmrs.sense_tag_json()
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
        print("Tagged JSON (with MFS): {}".format(dmrs.sense_tag_json_str()))

    def test_mrs_formats(self):
        text = "Some dogs chase some cats."
        a_sent = self.ERG.txt2dmrs(text)
        a_m = a_sent.mrses[0]
        # Create sentence object from raw data
        sent = Sentence(a_sent.text)
        sent.add(a_m.text)
        self.assertIsNotNone(sent)
        m = sent.mrses[0]
        self.assertEqual(len(sent), 1)
        self.assertEqual(str(m)[:20], '[ TOP: h0\n  INDEX: e')
        # now make DMRS XML ...
        xml_str = etree.tostring(m.sense_tag(with_raw=False)).decode('utf-8')
        self.assertTrue(xml_str.startswith('<dmrs cfrom="'))
        # add new DMRS from XML
        sent.add_from_xml(xml_str)
        self.assertEqual(len(sent), 2)  # now we should have 2 MRSes
        m2 = sent.mrses[1]
        # and they should look exactly the same
        xml_str2 = etree.tostring(m2.sense_tag(with_raw=False)).decode('utf-8')
        self.assertEqual(xml_str, xml_str2)
        print(xml_str2)
        pass

    def test_lelesk_integration(self):
        text = "A big bird is flying on the sky."
        a_sent = self.ERG.txt2dmrs(text)
        context = [p.pred.lemma for p in a_sent.mrses[0].mrs().eps()]
        preds = a_sent.mrses[0].mrs().eps()
        wsd = LeLeskWSD(dbcache=LeskCache().setup())
        for w, p in zip(context, preds):
            scores = wsd.lelesk_wsd(w, '', lemmatizing=False, context=context)
            if scores:
                print("Word: {w} (p={p}|{nid}) => {ss} | Score: {sc} | Def: {d}".format(w=w, p=str(p.pred), nid=p.nodeid, ss=scores[0].candidate.synset, sc=scores[0].score, d=scores[0].candidate.synset.glosses[0].text()))
            else:
                print("Word: {w} => N/A".format(w=w))

    def test_sensetag_using_lelesk(self):
        text = "A big bird is flying on the sky."
        print("Tagging ``{s}'' using lelesk".format(s=text))
        a_sent = self.ERG.txt2dmrs(text)
        js = a_sent.mrses[0].sense_tag_json_str(method='lelesk')
        print("Tagged JSON (using LeLesk): {}".format(js))

    def test_parse_no(self):
        text = "I saw a girl with a big telescope which is nice."
        a_sent = self.ERG.txt2dmrs(text)
        self.assertEqual(len(a_sent.mrses), 5)  # default is 5
        # increase parse count to 7
        a_sent = self.ERG.txt2dmrs(text, parse_count=7)
        self.assertEqual(len(a_sent.mrses), 7)
        # increase parse count to 10
        a_sent = self.ERG.txt2dmrs(text, parse_count=10)
        self.assertEqual(len(a_sent.mrses), 10)

########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
