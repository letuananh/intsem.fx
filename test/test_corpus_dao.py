#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Corpus DAO
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging
import unittest

from texttaglib.chirptext import ttl
from coolisf.util import sent2json
from coolisf import GrammarHub
from coolisf.dao import CorpusDAOSQLite
from coolisf.model import Document, Sentence

# -----------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------

from test import TEST_DATA
DB_FILE = os.path.join(TEST_DATA, 'test_corpus.db')


def getLogger():
    return logging.getLogger(__name__)


# -----------------------------------------------------------------------
# TEST SCRIPTS
# -----------------------------------------------------------------------

class TestDAOBase(unittest.TestCase):

    # We create a dummy corpora collection (visko unittest collection)
    corpus_name = 'corpus01'
    doc_name = 'doc01'
    ghub = GrammarHub()
    ERG = ghub.ERG
    db = CorpusDAOSQLite(":memory:", "memdb")
    realdb = CorpusDAOSQLite(DB_FILE, "col01")

    @classmethod
    def setUpClass(cls):
        logging.info("Preparing test data dir")
        if not os.path.exists(TEST_DATA):
            os.makedirs(TEST_DATA)
        if os.path.isfile(DB_FILE):
            os.unlink(DB_FILE)

    @classmethod
    def tearDownClass(cls):
        logging.debug("Cleaning up")

    def ensure_corpus(self, db, ctx):
        """ Ensure that testcorpus exists"""
        corpus = db.get_corpus(self.corpus_name, ctx=ctx)
        if corpus is None:
            db.create_corpus(self.corpus_name, ctx=ctx)
            corpus = db.get_corpus(self.corpus_name, ctx=ctx)
        return corpus

    def ensure_doc(self, db, ctx):
        """ Ensure that testcorpus exists"""
        corpus = self.ensure_corpus(db, ctx)
        doc = db.get_doc(self.doc_name, ctx=ctx)
        if doc is None:
            doc = corpus.new(self.doc_name)
            db.save_doc(doc, ctx=ctx)
        return doc

    def ensure_sent(self, db, ctx):
        doc = self.ensure_doc(db, ctx)
        sents = db.get_sents(doc.ID, ctx=ctx)
        if sents:
            return db.get_sent(sents[0].ID, ctx=ctx)
        else:
            sent = Sentence("I love you.")
            sent.add("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:1> LBL: h4 ARG0: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ]
          [ pronoun_q<0:1> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _love_v_1<2:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: h8 ]
          [ unknown<7:11> LBL: h9 ARG: x11 [ x PERS: 2 IND: + PT: std ] ARG0: e10 [ e SF: prop ] ]
          [ pron<7:11> LBL: h12 ARG0: x11 ]
          [ pronoun_q<7:11> LBL: h13 ARG0: x11 RSTR: h14 BODY: h15 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h8 qeq h9 h14 qeq h12 > ]""")
            sent.add("""[ TOP: h0
  INDEX: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ]
  RELS: < [ pron<0:1> LBL: h4 ARG0: x3 [ x PERS: 1 NUM: sg IND: + PT: std ] ]
          [ pronoun_q<0:1> LBL: h5 ARG0: x3 RSTR: h6 BODY: h7 ]
          [ _love_v_1<2:6> LBL: h1 ARG0: e2 ARG1: x3 ARG2: x8 [ x PERS: 2 IND: + PT: std ] ]
          [ pron<7:11> LBL: h9 ARG0: x8 ]
          [ pronoun_q<7:11> LBL: h10 ARG0: x8 RSTR: h11 BODY: h12 ] >
  HCONS: < h0 qeq h1 h6 qeq h4 h11 qeq h9 > ]""")
            doc.add(sent)
            dmrs = sent[0].dmrs()
            dmrs.tag_node(10002, '01775164-v', 'love', ttl.Tag.OTHER)
            sent.tag_xml()
            return db.save_sent(sent, ctx=ctx)


class TestDMRSSQLite(TestDAOBase):

    def test_create_a_corpus(self):
        print("Test creating a new corpus")
        with self.db.ctx() as ctx:
            self.ensure_corpus(self.db, ctx)
            corpus = self.db.get_corpus(self.corpus_name, ctx=ctx)
            self.assertIsNotNone(corpus)
            self.assertEqual(corpus.name, self.corpus_name)

    def test_create_a_doc(self):
        print("Test creating a new document")
        with self.db.ctx() as ctx:
            self.ensure_doc(self.db, ctx)
            doc = self.db.get_doc(self.doc_name, ctx=ctx)
            self.assertIsNotNone(doc)
            self.assertEqual(doc.name, self.doc_name)

    def test_create_sentence(self):
        logging.info("Test creating a new sentence")
        with self.db.ctx() as ctx:
            sid = self.ensure_sent(self.db, ctx).ID
            sent = self.db.get_sent(sid, ctx=ctx)
            dmrs = sent[0].dmrs()
            self.assertTrue(dmrs.tags[10002])

    def test_edit_doc_info(self):
        with self.db.ctx() as ctx:
            self.ensure_doc(self.db, ctx)
            doc = self.db.get_doc(self.doc_name, ctx=ctx)
            # clear info
            # Test store grammar, tagger, parse_count and lang
            doc.grammar = None
            doc.tagger = None
            doc.parse_count = None
            doc.lang = None
            self.db.save_doc(doc, ctx=ctx)
            doc = self.db.get_doc(self.doc_name, ctx=ctx)
            self.assertIsNone(doc.grammar)
            self.assertIsNone(doc.tagger)
            self.assertIsNone(doc.parse_count)
            self.assertIsNone(doc.lang)
            # Test store grammar, tagger, parse_count and lang
            doc.grammar = "ERG"
            doc.tagger = "lelesk"
            doc.parse_count = 5
            doc.lang = "en"
            self.db.save_doc(doc, ctx=ctx)
            doc = self.db.get_doc(self.doc_name, ctx=ctx)
            self.assertEqual(doc.grammar, "ERG")
            self.assertEqual(doc.tagger, "lelesk")
            self.assertEqual(doc.parse_count, 5)
            self.assertEqual(doc.lang, "en")

    def test_clone_sentence(self):
        print("Test cloning sentence")
        with self.db.ctx() as ctx:
            sent = self.ensure_sent(self.db, ctx)
            # clone the ensured sentence
            sent2 = Sentence(sent.text)
            sent2.docID = sent.docID
            sent2.add(str(sent[0]))
            sent2[0].dmrs().tags.update(sent[0].dmrs().tags)
            sent2.tag_xml()
            self.db.save_sent(sent2, ctx=ctx)
            # verify that there are 2 sentences
            sents = self.db.get_sents(sent.docID, ctx=ctx)
            self.assertEqual(len(sents), 2)
            s1, s2 = sents
            # verify dummy readings inside sentences
            self.assertEqual(s1.readings, [None, None])
            self.assertEqual(s2.readings, [None])
            # select actual data ...
            s1 = self.db.get_sent(s1.ID, ctx=ctx)
            s2 = self.db.get_sent(s2.ID, ctx=ctx)
            # verify raws
            self.assertTrue(s1[0].dmrs().raw)
            self.assertTrue(s2[0].dmrs().raw)
            self.assertEqual(s1[0].mrs().tostring(), s2[0].mrs().tostring())
            d1 = s1[0].dmrs()
            d2 = s2[0].dmrs()
            self.assertEqual(d1.tags[10002][0].synset.ID, d2.tags[10002][0].synset.ID)
            self.assertEqual(d1.tags[10002][0].synset.lemma, d2.tags[10002][0].synset.lemma)

    def test_modify_reading(self):
        with self.db.ctx() as ctx:
            sent = self.ensure_sent(self.db, ctx)
            r = sent[0]
            getLogger().debug(r.dmrs().preds())
            preds = ['pron_rel', 'pronoun_q_rel', '_love_v_1_rel', 'unknown_rel', 'pron_rel', 'pronoun_q_rel']
            self.assertEqual(r.dmrs().preds(), preds)
            # delete some nodes
            to_del = [n for n in r.dmrs().layout.nodes if n.predstr == 'pronoun_q' or n.predstr == 'unknown']
            r.dmrs().layout.delete(*to_del)
            r.dmrs().layout.save()
            r.sentID = sent.ID
            # update reading
            self.db.update_reading(r, ctx=ctx)
            # reread sentence from DB
            s2 = self.db.get_sent(sent.ID, ctx=ctx)
            preds2 = ['pron_rel', '_love_v_1_rel', 'pron_rel']
            self.assertEqual(s2[0].dmrs().preds(), preds2)

    def test_paging(self):
        with self.db.ctx() as ctx:
            sent = self.ensure_sent(self.db, ctx)
            # create 49 more sentences
            for idx in range(49):
                new_sent = Sentence(sent.text)
                new_sent.add(sent[0].mrs().tostring())
                new_sent.docID = sent.docID
                self.db.save_sent(new_sent, ctx=ctx)
            # now do paging
            all_sents = self.db.get_sents(sent.docID, ctx=ctx)
            self.assertEqual(len(all_sents), 50)
            page1 = self.db.get_sents(sent.docID, page=0, pagesize=30, ctx=ctx)
            self.assertEqual(len(page1), 30)
            self.assertEqual(page1[0].ID, 1)
            self.assertEqual(page1[-1].ID, 30)
            page2 = self.db.get_sents(sent.docID, page=1, pagesize=30, ctx=ctx)
            self.assertEqual(len(page2), 20)
            self.assertEqual(page2[0].ID, 31)
            self.assertEqual(page2[-1].ID, 50)


class TestCorpusManagement(TestDAOBase):

    def test_moving_sentences(self):
        with self.db.ctx() as ctx:
            corpus = self.db.create_corpus("test", ctx=ctx)
            doc_unk = corpus.new("default")
            doc_rain = corpus.new("rain")
            doc_dog = corpus.new("dog")
            for doc in corpus:
                self.db.save_doc(doc, ctx=ctx)
            docs = ctx.doc.select()
            # add sentences to default
            doc_unk.new("It rains.").add("""[ TOP: h0 RELS: < [ _rain_v_1<3:9> LBL: h1 ARG0: e2 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ] > HCONS: < h0 qeq h1 > ]""")
            doc_unk.new("It rained.").add("""[ TOP: h0 RELS: < [ _rain_v_1<3:10> LBL: h1 ARG0: e2 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ] ] > HCONS: < h0 qeq h1 > ]""")
            doc_unk.new("Some dog barks.").add("""[ TOP: h0 RELS: < [ _some_q_indiv<0:4> LBL: h1 ARG0: x4 [ x NUM: sg PERS: 3 IND: + ] RSTR: h6 ] [ _dog_n_1<5:8> LBL: h2 ARG0: x4 ] [ _bark_v_1<9:15> LBL: h3 ARG0: e5 [ e SF: prop TENSE: pres MOOD: indicative PROG: - PERF: - ] ARG1: x4 ] > HCONS: < h0 qeq h3 h6 qeq h2 > ]""")
            doc_unk.new("Some dog barked.").add("""[ TOP: h0 RELS: < [ _some_q_indiv<0:4> LBL: h1 ARG0: x4 [ x NUM: sg PERS: 3 IND: + ] RSTR: h6 ] [ _dog_n_1<5:8> LBL: h2 ARG0: x4 ] [ _bark_v_1<9:16> LBL: h3 ARG0: e5 [ e SF: prop TENSE: past MOOD: indicative PROG: - PERF: - ] ARG1: x4 ] > HCONS: < h0 qeq h3 h6 qeq h2 > ]""")
            doc_unk.new("Some dog has been barking.").add("""[ TOP: h0 RELS: < [ _some_q_indiv<0:4> LBL: h1 ARG0: x4 [ x NUM: sg PERS: 3 IND: + ] RSTR: h6 ] [ _dog_n_1<5:8> LBL: h2 ARG0: x4 ] [ _bark_v_1<18:26> LBL: h3 ARG0: e5 [ e SF: prop TENSE: pres MOOD: indicative PROG: + PERF: + ] ARG1: x4 ] > HCONS: < h0 qeq h3 h6 qeq h2 > ]""")
            for sent in doc_unk:
                self.db.save_sent(sent, ctx=ctx)
            unk_sents = self.db.get_sents(docID=doc_unk.ID, ctx=ctx)
            rain_sents = self.db.get_sents(docID=doc_rain.ID, ctx=ctx)
            dog_sents = self.db.get_sents(docID=doc_dog.ID, ctx=ctx)
            self.assertEqual(len(docs), 3)
            self.assertEqual(len(unk_sents), 5)
            self.assertEqual(len(rain_sents), 0)
            self.assertEqual(len(dog_sents), 0)
            sents = [self.db.get_sent(s.ID, ctx=ctx) for s in ctx.sentence.select()]
            for s in sents:
                if s[0].dmrs().layout.top.rplemma == 'rain':
                    s.docID = doc_rain.ID
                elif s[0].dmrs().layout.top.rplemma == 'bark':
                    s.docID = doc_dog.ID
                ctx.sentence.save(s, columns=('docID',))
            unk_sents = self.db.get_sents(docID=doc_unk.ID, ctx=ctx)
            rain_sents = self.db.get_sents(docID=doc_rain.ID, ctx=ctx)
            dog_sents = self.db.get_sents(docID=doc_dog.ID, ctx=ctx)
            self.assertEqual(len(unk_sents), 0)
            self.assertEqual(len(rain_sents), 2)
            self.assertEqual(len(dog_sents), 3)
            # move sentences around
        pass


SENT_TEXT = "ロボットの子は猫が好きです。"
SENT_TAGS = {'tokens': [{'text': 'ロボット', 'cto': 4, 'cfrom': 0}, {'text': 'の', 'cto': 6, 'cfrom': 5}, {'text': '子', 'cto': 8, 'cfrom': 7}, {'text': 'は', 'cto': 10, 'cfrom': 9}, {'text': '猫', 'cto': 12, 'cfrom': 11}, {'text': 'が', 'cto': 14, 'cfrom': 13}, {'text': '好き', 'cto': 17, 'cfrom': 15}, {'text': 'です', 'cto': 20, 'cfrom': 18}, {'text': '。', 'cto': 22, 'cfrom': 21}], 'concepts': [{'clemma': 'ロボット', 'tokens': [0], 'tag': '02761392-n'}, {'clemma': '猫', 'tokens': [4], 'tag': '02121620-n'}, {'clemma': '好き', 'tokens': [6], 'tag': '01292683-a'}, {'clemma': 'ロボットの子', 'tokens': [0, 1, 2], 'tag': '10285313-n', 'flag': 'E'}], 'text': 'ロボット の 子 は 猫 が 好き です 。 \n'}


class TestHumanAnnotation(TestDAOBase):

    def test_human_annotations(self):
        # ISF sentence
        sent = self.ghub.JACYMC.parse(SENT_TEXT, 1)
        sent.shallow = ttl.Sentence.from_json(SENT_TAGS)
        with self.db.ctx() as ctx:
            doc = self.ensure_doc(self.db, ctx)
            doc.add(sent)
            self.db.save_sent(sent, ctx=ctx)  # this should save the annotations as well
            # retrieve them
            sent2 = self.db.get_annotations(sent.ID, ctx=ctx)
            v2_json = sent2.shallow.to_json()
            # getLogger().debug("Words: {}".format(sent2.words))
            # getLogger().debug("Concepts: {}".format([(x, x.words) for x in sent2.concepts]))
            # getLogger().debug("v2_json: {}".format(v2_json))
            # compare to json_sent
            self.assertEqual(v2_json["text"], SENT_TAGS["text"])
            self.assertEqual(v2_json["tokens"], SENT_TAGS["tokens"])
            self.assertEqual(v2_json["concepts"], SENT_TAGS["concepts"])
            self.assertEqual(v2_json, SENT_TAGS)

    def test_commenting(self):
        with self.db.ctx() as ctx:
            doc = self.ensure_doc(self.db, ctx)
            sent = Sentence("This is an empty sentence.")
            doc.add(sent)
            note = "This sentence needs to be checked"
            sent.comment = note
            self.db.save_sent(sent, ctx=ctx)
            actual = self.db.read_note_sentence(sent.ID, ctx=ctx)
            self.assertEqual(note, actual)
            # update comment
            note2 = "This sentence has been checked"
            self.db.note_sentence(sent.ID, note2, ctx=ctx)
            actual = self.db.read_note_sentence(sent.ID, ctx=ctx)
            self.assertEqual(actual, note2)
            # note is retrieved together with other sentence's info
            sent = self.db.get_sent(sent.ID, ctx=ctx)
            self.assertEqual(sent.comment, note2)
            # comment is preserved in JSON
            sent_json = sent2json(sent)
            self.assertEqual(sent_json['comment'], note2)

    def test_get_prev_next(self):
        with self.db.ctx() as ctx:
            dao = self.db
            corpus = dao.create_corpus('test', ctx=ctx)
            doc1 = Document(name='doc1', corpusID=corpus.ID)
            dao.save_doc(doc1, ctx=ctx)
            doc2 = Document(name='doc2', corpusID=corpus.ID)
            dao.save_doc(doc2, ctx=ctx)
            dao.save_sent(Sentence(text="It rains.", docID=doc1.ID), ctx=ctx)
            dao.save_sent(Sentence(text="雨が降る。", docID=doc2.ID), ctx=ctx)
            dao.save_sent(Sentence(text="I like cats.", docID=doc1.ID), ctx=ctx)
            dao.save_sent(Sentence(text="猫が好きです。", docID=doc2.ID), ctx=ctx)
            dao.save_sent(Sentence(text="教師です。", docID=doc2.ID), ctx=ctx)
            dao.save_sent(Sentence(text="I'm a teacher.", docID=doc1.ID), ctx=ctx)
            dao.save_sent(Sentence(text="お休みなさい。", docID=doc2.ID), ctx=ctx)
            dao.save_sent(Sentence(text="Good night.", docID=doc1.ID), ctx=ctx)
            dao.flag_sent(2, Sentence.WARNING, ctx=ctx)
            dao.flag_sent(5, Sentence.WARNING, ctx=ctx)
            sents = ctx.sentence.select()
            self.assertEqual(len(sents), 8)
            # prev_sent
            self.assertEqual(dao.next_sentid(1, ctx=ctx), 3)
            self.assertEqual(dao.next_sentid(3, ctx=ctx), 6)
            self.assertEqual(dao.next_sentid(6, ctx=ctx), 8)
            self.assertEqual(dao.prev_sentid(7, ctx=ctx), 5)
            self.assertEqual(dao.prev_sentid(5, ctx=ctx), 4)
            self.assertEqual(dao.prev_sentid(4, ctx=ctx), 2)
            self.assertEqual(dao.prev_sentid(2, ctx=ctx), None)
            # next prev by flag
            self.assertEqual(dao.next_sentid(2, Sentence.WARNING, ctx=ctx), 5)
            self.assertEqual(dao.next_sentid(4, Sentence.WARNING, ctx=ctx), 5)
            self.assertEqual(dao.next_sentid(5, Sentence.WARNING, ctx=ctx), None)
            self.assertEqual(dao.prev_sentid(5, Sentence.WARNING, ctx=ctx), 2)
            self.assertEqual(dao.prev_sentid(2, Sentence.WARNING, ctx=ctx), None)


########################################################################

if __name__ == "__main__":
    unittest.main()
