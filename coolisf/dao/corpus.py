# -*- coding: utf-8 -*-

'''
Corpus DAO - ISF Corpus management functions
'''

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

# NOTE: This is used to be a parted of VisualKopasu, but relicensed
# & migrated into coolISF

import os
import os.path
import logging

from texttaglib.puchikarui import Schema, with_ctx
from texttaglib.chirptext import ttl

from coolisf.util import is_valid_name
from coolisf.model import Corpus, Document, Sentence, Reading
from coolisf.model import MRS, DMRS, DMRSLayout, Node, Sense, SortInfo, Link, Predicate
from coolisf.model import GpredValue, Lemma
from coolisf.model import Word, Concept, CWLink


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

logger = logging.getLogger(__name__)
MY_DIR = os.path.dirname(os.path.realpath(__file__))
INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'init_corpus.sql')


class RichKopasu(Schema):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_file(INIT_SCRIPT)
        self.add_table('corpus', ['ID', 'name', 'title'], proto=Corpus).set_id('ID')
        self.add_table('document', ['ID', 'name', 'corpusID', 'title',
                                    'grammar', 'tagger', 'parse_count', 'lang'],
                       proto=Document, alias='doc').set_id('ID')
        self.add_table('sentence', ['ID', 'ident', 'text', 'docID', 'flag', 'comment'],
                       proto=Sentence).set_id('ID')
        self.add_table('reading', ['ID', 'ident', 'mode', 'sentID', 'comment'],
                       proto=Reading).set_id('ID').field_map(ident='rid')
        self.add_table('mrs', ['ID', 'ident', 'raw', 'readingID'],
                       proto=MRS).set_id('ID')
        self.add_table('dmrs', ['ID', 'ident', 'cfrom', 'cto', 'surface', 'raw', 'readingID'],
                       proto=DMRS).set_id('ID')
        # Node related tables
        self.add_table('dmrs_node', ['ID', 'nodeid', 'cfrom', 'cto', 'surface', 'base',
                                     'carg', 'dmrsID', 'rplemmaID', 'rppos', 'rpsense',
                                     'gpred_valueID', 'synsetid', 'synset_score'],
                       proto=Node, alias='node').set_id('ID')
        self.add_table('dmrs_node_sortinfo', ['ID', 'cvarsort', 'num', 'pers', 'gend', 'sf',
                                              'tense', 'mood', 'prontype', 'prog', 'perf',
                                              'ind', 'dmrs_nodeID'],
                       proto=SortInfo, alias='sortinfo').set_id('ID')
        self.add_table('dmrs_node_gpred_value', ['ID', 'value'],
                       proto=GpredValue, alias='gpval').set_id('ID')
        self.add_table('dmrs_node_realpred_lemma', ['ID', 'lemma'],
                       proto=Lemma, alias='rplemma').set_id('ID')
        # Link related tables
        self.add_table('dmrs_link', ['ID', 'fromNodeID', 'toNodeID', 'dmrsID', 'post', 'rargname'],
                       proto=Link, alias='link').set_id('ID').field_map(fromNodeID="from_nodeid", toNodeID="to_nodeid")
        # Human annotation related tables
        self.add_table('word', ['ID', 'sid', 'widx', 'word', 'lemma', 'pos', 'cfrom', 'cto', 'comment'],
                       proto=Word).set_id('ID')
        self.add_table('concept', ['ID', 'sid', 'cidx', 'clemma', 'tag', 'flag', 'comment'],
                       proto=Concept).set_id('ID')
        self.add_table('cwl', ['cid', 'wid'],
                       proto=CWLink)


class CachedTable():
    '''
    ORM cache
    @auto_fill: Auto select all objects to cache when the cache is created
    '''
    def __init__(self, table, cache_by_field="value", ctx=None, auto_fill=True):
        self.cacheMap = {}
        self.cacheMapByID = {}
        self.table = table
        self.cache_by_field = cache_by_field
        if auto_fill:
            instances = self.table.select(ctx=ctx)
            if instances is not None:
                for instance in instances:
                    self.cache(instance)

    def cache(self, instance):
        if instance:
            key = getattr(instance, self.cache_by_field)
            if key not in self.cacheMap:
                self.cacheMap[key] = instance
            else:
                logger.debug(("Cache error: key [%s] exists!" % key))

            key = tuple(getattr(instance, c) for c in self.table.id_cols)
            if key not in self.cacheMapByID:
                self.cacheMapByID[key] = instance
            else:
                logger.debug(("Cache error: ID [%s] exists!" % key))

    def by_value(self, value, new_object=None, ctx=None):
        if value not in self.cacheMap:
            # insert a new record
            if new_object is None:
                # try to select from database first
                results = self.table.select_single("{f}=?".format(f=self.cache_by_field), (value,), ctx=ctx)
                if not results:
                    # create a new instance
                    new_object = self.table.to_obj((value,), (self.cache_by_field,))
                    self.table.save(new_object, ctx=ctx)
                    # select the instance again
                    new_object = self.table.select_single("{f}=?".format(f=self.cache_by_field), (value,), ctx=ctx)
                else:
                    new_object = results  # Use the object from DB
            self.cache(new_object)
        return self.cacheMap[value]

    def by_id(self, *ID, ctx=None):
        k = tuple(ID)
        if k not in self.cacheMapByID:
            # select from database
            obj = self.table.by_id(*ID, ctx=ctx)
            self.cache(obj)
        return self.cacheMapByID[k]


class CorpusDAOSQLite(RichKopasu):

    def __init__(self, data_source=":memory:", name='', auto_fill=False, *args, **kwargs):
        super().__init__(data_source, *args, **kwargs)
        self.name = name
        self.lemmaCache = CachedTable(self.rplemma, "lemma", auto_fill=auto_fill)
        self.gpredCache = CachedTable(self.gpval, "value", auto_fill=auto_fill)

    @property
    def db_path(self):
        return self.ds.path

    @with_ctx
    def get_corpus(self, corpus_name, ctx=None):
        return ctx.corpus.select_single('name=?', (corpus_name,))

    @with_ctx
    def create_corpus(self, corpus_name, ctx=None):
        if not is_valid_name(corpus_name):
            raise Exception("Invalid corpus name (provided: {}) - Visko only accept names using alphanumeric characters".format(corpus_name))
        corpus = Corpus(corpus_name)
        corpus.ID = ctx.corpus.save(corpus)
        return corpus

    @with_ctx
    def save_doc(self, doc, *fields, ctx=None):
        if not is_valid_name(doc.name):
            raise ValueError("Invalid doc name (provided: {}) - Visko only accept names using alphanumeric characters".format(doc.name))
        else:
            doc.ID = self.doc.save(doc, fields, ctx=ctx)
        return doc

    @with_ctx
    def get_docs(self, corpusID, ctx=None):
        corpus = ctx.corpus.by_id(corpusID)
        docs = ctx.doc.select('corpusID=?', (corpus.ID,))
        for doc in docs:
            doc.corpus = corpus
            q = "SELECT COUNT(*) FROM sentence WHERE docID = ?"
            p = (doc.ID,)
            doc.sent_count = ctx.select_scalar(q, p)
        return docs

    @with_ctx
    def get_doc(self, doc_name, ctx=None):
        # doc.name is unique
        doc = ctx.doc.select_single('name=?', (doc_name,))
        if doc is None:
            return None
        doc.corpus = ctx.corpus.by_id(doc.corpusID)
        q = "SELECT COUNT(*) FROM sentence WHERE docID = ?"
        p = (doc.ID,)
        doc.sent_count = ctx.select_scalar(q, p)
        return doc

    @with_ctx
    def get_sents(self, docID, flag=None, add_dummy_parses=True, page=None, pagesize=1000, ctx=None):
        where = ['docID = ?']
        params = [docID]
        limit = None
        if flag is not None:
            where.append('flag = ?')
            params.append(flag)
        if page is not None:
            offset = page * pagesize
            limit = "{}, {}".format(offset, pagesize)
        sents = ctx.sentence.select(' AND '.join(where), params, limit=limit)
        if add_dummy_parses:
            for sent in sents:
                reading_count = ctx.select_scalar('SELECT COUNT(*) FROM reading WHERE sentid=?', (sent.ID,))
                sent.readings = [None] * reading_count
        return sents

    @with_ctx
    def note_sentence(self, sent_id, comment, ctx=None):
        # save comments
        return ctx.sentence.update((comment,), 'ID=?', (sent_id,), ['comment'])

    @with_ctx
    def read_note_sentence(self, sent_id, ctx=None):
        return ctx.sentence.by_id(sent_id, columns=['comment']).comment

    @with_ctx
    def save_sent(self, a_sentence, ctx=None):
        """
        Save sentence object (with all DMRSes, raws & shallow readings inside)
        """
        # validations
        if a_sentence is None:
            raise ValueError("Sentence object cannot be None")
        # ctx is not None now
        if not a_sentence.ID:
            # choose a new ident
            if a_sentence.ident is None or a_sentence.ident in (-1, '-1', ''):
                # create a new ident (it must be a string)
                a_sentence.ident = str(ctx.select_scalar('SELECT IFNULL(max(rowid), 0)+1 FROM sentence'))
            if a_sentence.ident is None:
                a_sentence.ident = "1"
            # save sentence
            a_sentence.ID = ctx.sentence.save(a_sentence)
            # save shallow
            if a_sentence.shallow is not None:
                self.save_annotations(a_sentence, ctx=ctx)
            # save readings
            for idx, reading in enumerate(a_sentence.readings):
                if reading.rid is None:
                    reading.rid = idx
                # Update sentID
                reading.sentID = a_sentence.ID
                self.save_reading(reading, ctx=ctx)
        else:
            # update sentence
            pass
        # Select sentence
        return a_sentence

    @with_ctx
    def save_reading(self, reading, ctx=None):
        # save or update reading info
        reading.ID = ctx.reading.save(reading) if reading.ID is None else reading.ID
        # Save DMRS
        dmrs = reading.dmrs()
        # store raw if needed
        if dmrs.raw is None:
            dmrs.raw = dmrs.xml_str(pretty_print=False)

        dmrs.readingID = reading.ID
        if dmrs.ident is None:
            dmrs.ident = reading.rid
        dmrs.ID = None  # reset DMRS ID
        dmrs.ID = ctx.dmrs.save(dmrs)
        # nodes and links are in layout
        # save nodes
        for node in dmrs.layout.nodes:
            node.dmrsID = dmrs.ID
            # save realpred
            node.pred = node.predstr
            if node.rplemma:
                # Escape lemma
                lemma = self.lemmaCache.by_value(node.rplemma, ctx=ctx)
                node.rplemmaID = lemma.ID
            # save gpred
            if node.gpred:
                gpred_value = self.gpredCache.by_value(node.gpred, ctx=ctx)
                node.gpred_valueID = gpred_value.ID
            # save sense
            if node.sense:
                node.synsetid = node.sense.synsetid
                node.synset_score = node.sense.score
            elif node.nodeid in dmrs.tags:
                tags = dmrs.tags[node.nodeid]
                tag = tags[0]
                for t in tags[1:]:
                    if t.method == ttl.Tag.GOLD:
                        tag = t
                        break
                node.synsetid = tag.synset.ID.to_canonical()
                node.synset_score = tag.synset.tagcount
            # reset node ID
            node.ID = None
            node.ID = ctx.node.save(node)
            # save sortinfo
            node.sortinfo.dmrs_nodeID = node.ID
            node.sortinfo.ID = None  # reset sortinfo ID
            ctx.sortinfo.save(node.sortinfo)
        # save links
        for link in dmrs.layout.links:
            link.dmrsID = dmrs.ID
            if link.rargname is None:
                link.rargname = ''
            link.ID = None  # reset link ID
            link.ID = ctx.link.save(link)

    @with_ctx
    def get_reading(self, a_reading, ctx=None):
        # retrieve all DMRSes
        # right now, only 1 DMRS per reading
        a_dmrs = ctx.dmrs.select_single('readingID=?', (a_reading.ID,))
        a_reading._dmrs = a_dmrs
        a_dmrs.reading = a_reading
        a_dmrs._layout = DMRSLayout(source=a_dmrs)
        # retrieve all nodes
        nodes = ctx.node.select('dmrsID=?', (a_dmrs.ID,))
        for a_node in nodes:
            # retrieve sortinfo
            sortinfo = ctx.sortinfo.select_single('dmrs_nodeID=?', (a_node.ID,))
            if sortinfo is not None:
                a_node.sortinfo = sortinfo
            if a_node.rplemmaID is not None:
                # is a realpred
                a_node.rplemma = self.lemmaCache.by_id(int(a_node.rplemmaID), ctx=ctx).lemma
                a_node.pred = Predicate(Predicate.REALPRED, a_node.rplemma, a_node.rppos, a_node.rpsense)
            if a_node.gpred_valueID:
                # is a gpred
                a_node.pred = self.gpredCache.by_id(int(a_node.gpred_valueID), ctx=ctx).value
                # a_node.pred = Predicate.from_string(a_node.gpred)
            # create sense object
            if a_node.synsetid:
                sense = Sense()
                sense.synsetid = a_node.synsetid
                sense.score = a_node.synset_score
                sense.lemma = a_node.rplemma if a_node.rplemma else ''  # this also?
                sense.pos = a_node.synsetid[-1]  # Do we really need this?
                a_node.sense = sense
                a_dmrs.tag_node(a_node.nodeid, sense.synsetid, sense.lemma, ttl.Tag.DEFAULT, sense.score)
            a_dmrs.layout.add_node(a_node)
            # next node ...
        # retrieve all links
        links = ctx.link.select('dmrsID=?', (a_dmrs.ID,))
        for link in links:
            a_dmrs.layout.add_link(link)
        return a_reading

    @with_ctx
    def delete_reading(self, readingID, ctx=None):
        # delete all DMRS link, node
        ctx.dmrs_link.delete('dmrsID IN (SELECT ID FROM dmrs WHERE readingID=?)', (readingID,))
        ctx.dmrs_node_sortinfo.delete('dmrs_nodeID IN (SELECT ID FROM dmrs_node WHERE dmrsID IN (SELECT ID from dmrs WHERE readingID=?))', (readingID,))

        ctx.dmrs_node.delete('dmrsID IN (SELECT ID FROM dmrs WHERE readingID=?)', (readingID,))
        # delete all DMRS
        ctx.dmrs.delete("readingID=?", (readingID,))
        # delete readings
        ctx.reading.delete("ID=?", (readingID,))

    @with_ctx
    def update_reading(self, reading, ctx=None):
        # delete all DMRS link, node
        ctx.dmrs_link.delete('dmrsID IN (SELECT ID FROM dmrs WHERE readingID=?)', (reading.ID,))
        ctx.dmrs_node_sortinfo.delete('dmrs_nodeID IN (SELECT ID FROM dmrs_node WHERE dmrsID IN (SELECT ID from dmrs WHERE readingID=?))', (reading.ID,))

        ctx.dmrs_node.delete('dmrsID IN (SELECT ID FROM dmrs WHERE readingID=?)', (reading.ID,))
        # delete all DMRS
        ctx.dmrs.delete("readingID=?", (reading.ID,))
        # update reading info
        self.save_reading(reading, ctx=ctx)

    @with_ctx
    def build_search_result(self, rows, with_comment=True, ctx=None):
        ''' build search result from query results
        Format: sentID, readingID, text, sentence_ident, docID, doc_name, corpus_name, corpusID
        '''
        if rows:
            logger.debug(("Found: %s presentation(s)" % len(rows)))
        else:
            logger.debug("None was found!")
            return []
        sentences = []
        sentences_by_id = {}
        for row in rows:
            readingID = row['readingID']
            sentID = row['sentID']
            sentence_ident = row['sentence_ident']
            text = row['text']
            docID = row['docID']
            if sentID in sentences_by_id:
                # sentence exists, add this reading to that sentence
                a_reading = Reading(ID=readingID)
                # self.get_reading(a_reading)
                sentences_by_id[sentID].readings.append(a_reading)
            else:
                a_sentence = Sentence(ident=sentence_ident, text=text, docID=docID, ID=sentID)
                a_sentence.corpus = Corpus(name=row['corpus_name'], ID=row['corpusID'])
                a_sentence.doc = Document(name=row['doc_name'], ID=docID)
                if readingID:
                    # add reading if needed
                    a_reading = Reading(ID=readingID)
                    a_sentence.readings.append(a_reading)
                sentences.append(a_sentence)
                sentences_by_id[sentID] = a_sentence
        logger.debug(("Sentence count: %s" % len(sentences)))
        if with_comment:
            for sent in sentences:
                sent.comment = self.read_note_sentence(sent_id=sent.ID, ctx=ctx)
        return sentences

    @with_ctx
    def get_sent(self, sentID, mode=None, readingIDs=None, skip_details=False, ctx=None):
        a_sentence = ctx.sentence.by_id(sentID)
        if a_sentence is not None:
            self.get_annotations(sentID, a_sentence, ctx=ctx)
            # retrieve all readings
            conditions = 'sentID=?'
            params = [a_sentence.ID]
            if mode:
                conditions += ' AND mode=?'
                params.append(mode)
            if readingIDs and len(readingIDs) > 0:
                conditions += ' AND ID IN ({params_holder})'.format(params_holder=",".join((["?"] * len(readingIDs))))
                params.extend(readingIDs)
            readings = ctx.reading.select(conditions, params)
            for r in readings:
                r.sent = a_sentence
                a_sentence.readings.append(r)
            for a_reading in a_sentence.readings:
                if not skip_details:
                    self.get_reading(a_reading, ctx=ctx)
        else:
            logging.debug("No sentence with ID={} was found".format(sentID))
        # Return
        return a_sentence

    @with_ctx
    def delete_sent(self, sentID, ctx=None):
        # delete all reading
        sent = self.get_sent(sentID, skip_details=True, ctx=ctx)
        # delete readings
        if sent is not None:
            for i in sent:
                self.delete_reading(i.ID, ctx=ctx)
        # delete words, concepts, cwl
        ctx.word.delete('sid=?', (sentID,))
        ctx.cwl.delete('cid IN (SELECT cid FROM concept WHERE sid=?)', (sentID,))
        ctx.concept.delete('sid=?', (sentID,))
        # delete sentence obj
        ctx.sentence.delete("ID=?", (sentID,))

    @with_ctx
    def get_annotations(self, sentID, sent_obj=None, ctx=None):
        if sent_obj is None:
            sent_obj = self.get_sent(sentID, skip_details=True, ctx=ctx)
        # select words
        # select concepts
        sent_obj.words = ctx.word.select("sid=?", (sentID,))
        wmap = {w.ID: w for w in sent_obj.words}
        sent_obj.concepts = ctx.concept.select("sid=?", (sentID,))
        cmap = {c.ID: c for c in sent_obj.concepts}
        # link concept-word
        links = ctx.cwl.select("cid IN (SELECT ID from concept WHERE sid=?)", (sentID,))
        for lnk in links:
            cmap[lnk.cid].words.append(wmap[lnk.wid])
        return sent_obj

    @with_ctx
    def save_annotations(self, sent_obj, ctx=None):
        for word in sent_obj.words:
            word.sid = sent_obj.ID
            word.ID = ctx.word.save(word)
        for concept in sent_obj.concepts:
            concept.sid = sent_obj.ID
            concept.ID = ctx.concept.save(concept)
            for word in concept.words:
                # save links
                logger.debug("Saving", CWLink(wid=word.ID, cid=concept.ID))
                ctx.cwl.save(CWLink(wid=word.ID, cid=concept.ID))
                pass

    @with_ctx
    def flag_sent(self, sid, flag, ctx=None):
        # update flag
        return ctx.sentence.update(new_values=(flag,), where='ID=?', where_values=(sid,), columns=('flag',))

    @with_ctx
    def next_sentid(self, sid, flag=None, ctx=None):
        sent_obj = ctx.sentence.by_id(sid, columns=('ID', 'docID'))
        docid = sent_obj.docID
        where = 'ID > ? AND docID == ?'
        params = [sid, docid]
        if flag is not None:
            where += " AND flag = ?"
            params.append(flag)
        next_sent = ctx.sentence.select_single(where=where, values=params, orderby="docID, ID", limit=1)
        return next_sent.ID if next_sent is not None else None

    @with_ctx
    def prev_sentid(self, sid, flag=None, ctx=None):
        sent_obj = ctx.sentence.by_id(sid, columns=('ID', 'docID'))
        docid = sent_obj.docID
        where = 'ID < ? AND docID == ?'
        params = [sid, docid]
        if flag is not None:
            where += " AND flag = ?"
            params.append(flag)
        prev_sent = ctx.sentence.select_single(where=where, values=params, orderby="docID DESC, ID DESC", limit=1)
        return prev_sent.ID if prev_sent is not None else None
