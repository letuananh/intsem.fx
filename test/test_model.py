#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script for testing coolisf models
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import unittest
import logging

from texttaglib.chirptext import header
from texttaglib.chirptext import texttaglib as ttl

from coolisf import GrammarHub
from coolisf.util import is_valid_name, sent2json
from coolisf.model import Corpus, Document, Sentence, Reading
from coolisf.model import DMRSLayout, Node, Link, Predicate, Pred, Triplet, Synset, SenseTag


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# TEST SCRIPTS
# -------------------------------------------------------------------------------

class TestModels(unittest.TestCase):

    def test_sensetag_objects(self):
        tag1 = SenseTag(Synset("00001740-n"), ttl.Tag.LELESK)
        tag2 = SenseTag(Synset("00001740-n"), ttl.Tag.LELESK)
        l = [tag1]
        print(tag1 == tag2)
        print(tag2 in l)


class TestSentenceModel(unittest.TestCase):

    ghub = GrammarHub()
    EI = ghub.ERG_ISF

    def test_sent(self):
        header("Test model")
        doc = Document("test")
        s = doc.new("It rains.")
        s.add("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]""")
        # test full work flow:
        #   mrs_str > dmrs() > xml > layout > dmrs > mrs > mrs_str
        expected = """[ TOP: h0 RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ] > HCONS: < h0 qeq h1 > ]"""
        actual = DMRSLayout.from_xml(s[0].edit().to_dmrs().xml()).to_dmrs().to_mrs().tostring(False)
        self.assertEqual(actual, expected)
        # Test different formats
        xstr = s.to_xml_str()
        self.assertTrue(xstr)
        lts = s.to_latex()  # LaTeX scripts
        self.assertTrue(lts)

    def test_convert(self):
        print("Test convert DMRSLayout to and from XML")
        dmrs = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]""").dmrs()
        layout = DMRSLayout.from_xml(dmrs.xml())
        self.assertEqual(dmrs.layout.to_json(), layout.to_json())

    def test_dmrs(self):
        header("Test building a DMRS from scratch")
        corpus = Corpus(name="manual")
        doc = corpus.new(name="testdoc")
        sent = doc.new("It rains.")
        self.assertIsInstance(sent, Sentence)
        reading = sent.add('[]')
        dmrs = reading.dmrs()
        l = dmrs.layout
        n = Node(10000, "_rain_v_1", 3, 9)
        n.sortinfo.update({'sf': 'prop', 'tense': 'pres', 'mood': 'indicative',
                           'prog': '-', 'perf': '-', 'sarcasm': '-'})
        l.add_node(n)
        l.add_link(Link(0, 10000, '', 'H'))  # this is top
        l.save()
        # sense tag the DMRS
        sent.tag(ttl.Tag.MFS)
        self.assertGreaterEqual(len(dmrs.tags), 1)
        self.assertTrue(sent.to_xml_str())

    def test_to_latex(self):
        dmrs = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]""").dmrs()
        print(dmrs.latex())

    def test_sent2json(self):
        sent = Sentence('It rains.')
        sent.add("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]""")
        j = sent2json(sent)
        print(j)

    def test_xml_encoding(self):
        print("Test XML to and from Sentence")
        sent = Sentence('It rains.')
        sent.add("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 ] >
  HCONS: < h0 qeq h1 > ]""").dmrs()
        sent.tag_xml(method=ttl.Tag.MFS)
        full_xml = sent.to_xml_str()
        compact_xml = sent.to_xml_str(pretty_print=False, with_dmrs=False)
        full_sent = Sentence.from_xml_str(full_xml)
        compact_sent = Sentence.from_xml_str(compact_xml)
        self.assertEqual(full_sent[0].dmrs().layout.to_json(), sent[0].dmrs().layout.to_json())
        self.assertEqual(compact_sent[0].dmrs().layout.to_json(), sent[0].dmrs().layout.to_json())


class TestDMRSModel(unittest.TestCase):

    def test_node(self):
        n = Node()
        n.rplemma = "foo"
        n.rppos = "n"
        n.rpsense = "1"
        print(n)

    def test_doc_xml(self):
        doc = Document("test")
        doc.new("It rains.", ident="1000").add("""[ TOP: h0 RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ] > HCONS: < h0 qeq h1 > ]""")
        doc.new("It rained.", ident="1010").add("""[ TOP: h0 RELS: < [ _rain_v_1<3:10> LBL: h1 ARG0: e2 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ] ] > HCONS: < h0 qeq h1 > ]""")
        doc.new("Some dog barks.", ident="1020").add("""[ TOP: h0 RELS: < [ _some_q_indiv<0:4> LBL: h1 ARG0: x4 [ x NUM: sg PERS: 3 IND: + ] RSTR: h6 ] [ _dog_n_1<5:8> LBL: h2 ARG0: x4 ] [ _bark_v_1<9:15> LBL: h3 ARG0: e5 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x4 ] > HCONS: < h0 qeq h3 h6 qeq h2 > ]""")
        doc.new("Some dog barked.", ident="1030").add("""[ TOP: h0 RELS: < [ _some_q_indiv<0:4> LBL: h1 ARG0: x4 [ x NUM: sg PERS: 3 IND: + ] RSTR: h6 ] [ _dog_n_1<5:8> LBL: h2 ARG0: x4 ] [ _bark_v_1<9:16> LBL: h3 ARG0: e5 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ] ARG1: x4 ] > HCONS: < h0 qeq h3 h6 qeq h2 > ]""")
        doc.new("Some dog has been barking.", ident="1040").add("""[ TOP: h0 RELS: < [ _some_q_indiv<0:4> LBL: h1 ARG0: x4 [ x NUM: sg PERS: 3 IND: + ] RSTR: h6 ] [ _dog_n_1<5:8> LBL: h2 ARG0: x4 ] [ _bark_v_1<18:26> LBL: h3 ARG0: e5 [ e SF: prop TENSE: pres MOOD: indicative PROG: + PERF: + ] ARG1: x4 ] > HCONS: < h0 qeq h3 h6 qeq h2 > ]""")
        idents = [s.ident for s in doc]
        dstr = doc.to_xml_str(pretty_print=False, with_dmrs=False)
        # convert XML string into a new document object
        doc2 = Document.from_xml_str(dstr)
        self.assertEqual(len(doc2), 5)
        idents2 = [s.ident for s in doc2]
        for s in doc2:
            self.assertIsNotNone(s[0].mrs())
        self.assertEqual(idents, idents2)

    def test_wsd(self):
        r = Reading("""[ TOP: h0 INDEX: e2 [ e SF: prop-or-ques ] RELS: < [ unknown_rel<0:34> LBL: h1 ARG: x4 [ x PERS: 3 NUM: sg ] ARG0: e2 ] [ _the_q_rel<0:3> LBL: h5 ARG0: x4 RSTR: h6 BODY: h7 ] [ "_adventure_n_1_rel"<4:13> LBL: h8 ARG0: x4 ] [ _of_p_rel<14:16> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x4 ARG2: x10 [ x PERS: 3 NUM: sg ] ] [ _the_q_rel<17:20> LBL: h11 ARG0: x10 RSTR: h12 BODY: h13 ] [ "_speckled/JJ_u_unknown_rel"<21:29> LBL: h14 ARG0: e15 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x10 ] [ "_band_n_1_rel"<30:34> LBL: h14 ARG0: x10 ] > HCONS: < h0 qeq h1 h6 qeq h8 h12 qeq h14 > ]""")
        context = list(r.dmrs().get_wsd_context())
        expected = ['the', 'adventure', 'of', 'the', 'speckled', 'band']
        self.assertEqual(expected, context)


class TestDMRSLayout(unittest.TestCase):

    sent = """[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:2> LBL: h4 ARG0: x3 [ x PERS: 3 NUM: sg GEND: n PT: std ] ]
          [ pronoun_q<0:2> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _be_v_id<3:5> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 3 NUM: sg IND: + ] ]
          [ _a_q<6:7> LBL: h9 ARG0: x8 RSTR: h10 BODY: h11 ]
          [ _blue_a_1<8:12> LBL: h12 ARG0: e13 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x8 ]
          [ compound<13:23> LBL: h12 ARG0: e14 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG1: x8 ARG2: x15 [ x IND: + PT: notpro ] ]
          [ udef_q<13:18> LBL: h16 ARG0: x15 RSTR: h17 BODY: h18 ]
          [ _guard_n_1<13:18> LBL: h19 ARG0: x15 ]
          [ _dog_n_1<19:23> LBL: h12 ARG0: x8 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h10 qeq h12 h17 qeq h19 > ]"""
    guard_dog = """[ TOP: h0 RELS: < [ compound<0:9> LBL: h1 ARG0: e4 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: x6 [ x IND: + NUM: sg PERS: 3 ] ARG2: x5 [ x IND: + PT: notpro ] ] [ udef_q<0:5> LBL: h2 ARG0: x5 RSTR: h7 ] [ _guard_n_1<0:5> LBL: h3 ARG0: x5 ] [ _dog_n_1<6:9> LBL: h1 ARG0: x6 ] > HCONS: < h0 qeq h1 h7 qeq h3 > ]"""

    def test_predicate(self):
        p = 'unknown'
        self.assertEqual(str(Predicate.from_string(p)), p)
        p = 'compound_rel'
        self.assertEqual(str(Predicate.from_string(p)), 'compound')  # without _rel
        p = 'udef_q'
        self.assertEqual(str(Predicate.from_string(p)), p)
        p = '_dog_n_1'
        self.assertEqual(str(Predicate.from_string(p)), p)

    def test_exploring_structure(self):
        r = Reading(self.sent)
        d = r.dmrs()
        p = d.obj().eps()[2]
        self.assertIn('ARG0', p.args)

    def test_pydelphin_pred(self):
        p = Pred.string_or_grammar_pred('unknown')
        self.assertEqual((p.type, p.lemma, p.pos, p.sense), (0, 'unknown', None, None))
        p = Pred.string_or_grammar_pred('udef_q')
        self.assertEqual((p.type, p.lemma, p.pos, p.sense), (0, 'udef', 'q', None))
        p = Pred.string_or_grammar_pred('_dog_n_1')
        self.assertEqual((p.type, p.lemma, p.pos, p.sense), (Pred.STRINGPRED, 'dog', 'n', '1'))
        p = Pred.realpred('dog', 'n', 1)
        self.assertEqual((p.type, p.lemma, p.pos, p.sense), (Pred.REALPRED, 'dog', 'n', '1'))
        p = Pred.string_or_grammar_pred('proper_q')
        self.assertEqual(p, 'proper_q_rel')
        self.assertEqual(p, 'proper_q')
        self.assertTrue(p in ('unknown_rel', 'proper_q_rel'))
        p = Pred.string_or_grammar_pred('compound_rel')
        self.assertEqual(p, 'compound')

    def test_delete(self):
        r = Reading(self.guard_dog)
        print(r.mrs().tostring(False))
        l = r.dmrs().layout
        l.delete(10000, 10001).save()
        preds = r.dmrs().preds()
        self.assertEqual(preds, ['_guard_n_1_rel', '_dog_n_1_rel'])

    def test_edit_partial_dmrs(self):
        r = Reading("""[ TOP: h0 RELS: < [ unknown<0:3> LBL: h1 ARG0: e2 [ e SF: prop-or-ques ] ] [ _yet_a_rel<0:3> LBL: h1 ARG0: e3 [ e MOOD: indicative SF: prop TENSE: untensed ] ARG1: e2 ] > HCONS: < h0 qeq h1 > ]""")
        l = r.dmrs().layout
        l.delete(l.head())
        self.assertEqual(l.to_dmrs().preds(), ['_yet_a_rel'])

    def test_get_top(self):
        sent = Reading(self.sent)
        e = sent.dmrs().edit()
        self.assertIsNotNone(e.top)
        self.assertEqual(e.head().predstr, "_be_v_id")
        # construction
        s = Reading(self.guard_dog)
        se = s.dmrs().edit()
        self.assertIsNotNone(se.top)
        self.assertEqual(se.top.predstr, "_dog_n_1")

    def test_shift_head(self):
        l = Reading("""[ TOP: h0 RELS: < [ unknown<0:6> LBL: h1 ARG0: e3 [ e SF: prop-or-ques ] ] [ _bare_a_1_rel<0:6> LBL: h2 ARG0: e4 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ] > HCONS: < h0 qeq h1 > ]""").dmrs().layout
        l.delete(l.head())  # delete unknown_rel
        self.assertIsNone(l.head())  # head should be empty now
        l.add_link(Link(0, 10001, '', 'H'))  # top point to _bare_a_1
        self.assertEqual(l.head().predstr, "_bare_a_1")

    def test_to_graph(self):
        struct = Reading(self.guard_dog).dmrs()
        sed = struct.edit()
        sed.top = 10003
        g = sed.top.to_graph()
        self.assertEqual(g, Triplet(name='_dog_n_1', in_links=frozenset({('ARG1/EQ', Triplet(name='compound', in_links=frozenset(), out_links=frozenset({('ARG2/NEQ', Triplet(name='_guard_n_1', in_links=frozenset({('RSTR/H', Triplet(name='udef_q', in_links=frozenset(), out_links=frozenset()))}), out_links=frozenset()))})))}), out_links=None))
        # make+a+face graph
        d = Reading("""[ TOP: h0
  RELS: < [ _make_v_1<0:4> LBL: h1 ARG0: e4 [ e SF: prop TENSE: untensed MOOD: indicative PROG: - PERF: - ] ARG2: x5 [ x NUM: sg PERS: 3 IND: + ] ]
          [ _a_q<5:6> LBL: h2 ARG0: x5 RSTR: h6 ]
          [ _face_n_1<7:11> LBL: h3 ARG0: x5 ] >
  HCONS: < h0 qeq h1 h6 qeq h3 > ]""").dmrs().layout
        h = d.head()
        g = h.to_graph(scan_outlinks=True)
        self.assertEqual(g, Triplet(name='_make_v_1', in_links=frozenset(), out_links=frozenset({('ARG2/NEQ', Triplet(name='_face_n_1', in_links=frozenset({('RSTR/H', Triplet(name='_a_q', in_links=frozenset(), out_links=frozenset()))}), out_links=frozenset()))})))

    def test_cfrom_cto(self):
        constr = Reading(self.guard_dog).dmrs()
        ce = constr.edit()
        self.assertEqual(len(ce.nodes), 4)
        self.assertEqual(ce[10000]['ARG1'].predstr, "_dog_n_1")
        self.assertEqual(ce[10000]['ARG2'].predstr, "_guard_n_1")

    def test_subgraph(self):
        # load a sample sentencce
        sent = Reading(self.sent).dmrs().layout
        # load construction
        struct = Reading(self.guard_dog)
        sed = struct.dmrs().edit()
        # look for construction in given sentence
        sub = sent.subgraph(sent[10008], constraints=sed)
        # The structure now should be exactly the same
        sg = sub.top.to_graph()
        seg = sed.top.to_graph()
        self.assertEqual(sg, seg)


class TestName(unittest.TestCase):

    def test_valid_name(self):
        self.assertTrue(is_valid_name('test'))
        self.assertTrue(is_valid_name('test123'))
        self.assertTrue(is_valid_name('1'))
        self.assertTrue(is_valid_name('1234'))
        self.assertTrue(is_valid_name('12_34'))
        self.assertTrue(is_valid_name('ABC12_34'))
        # invalid names
        self.assertFalse(is_valid_name(''))
        self.assertFalse(is_valid_name(None))
        self.assertFalse(is_valid_name('a.b'))


########################################################################

if __name__ == "__main__":
    unittest.main()
