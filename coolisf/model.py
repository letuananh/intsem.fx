# -*- coding: utf-8 -*-

"""
ISF data models
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import copy
import json
import gzip
import codecs
import logging
import itertools
# import threading
from collections import defaultdict as dd
from collections import namedtuple
from lxml import etree
# delphin
from delphin.extra.latex import dmrs_tikz_dependency
from delphin.mrs import simplemrs
from delphin.mrs import simpledmrs
from delphin.mrs import dmrx
from delphin.mrs import Mrs
from delphin.mrs import Dmrs
from delphin.mrs.components import Pred
from delphin.mrs.components import normalize_pred_string

from texttaglib.chirptext.anhxa import update_obj
from texttaglib.chirptext.leutile import StringTool, header
from texttaglib.chirptext import texttaglib as ttl
from yawlib import Synset
from lelesk import LeLeskWSD
from lelesk import LeskCache  # WSDResources

from coolisf.common import read_file, get_ep_lemma
from coolisf.parsers import parse_dmrs_str
from coolisf.mappings import PredSense


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------

class Corpus(object):
    """
    A corpus wrapper
    """
    def __init__(self, name='', title='', ID=None):
        self.ID = ID
        self.name = name
        self.title = title
        self.documents = []
        pass

    def new(self, name):
        """ Create a new document and add it to this corpus """
        doc = Document(name=name)
        doc.corpusID = self.ID
        self.documents.append(doc)
        return doc

    def __getitem__(self, idx):
        return self.documents[idx]

    def __len__(self):
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)

    def __repr__(self):
        return "Corpus(name={})".format(repr(self.name))


class Document(object):

    def __init__(self, name='', corpusID=None, title='', grammar=None, tagger=None, parse_count=None, lang=None, ID=None):
        self.ID = ID
        self.name = name
        self.corpusID = corpusID
        self.title = title if title else name
        self.grammar = grammar
        self.tagger = tagger
        self.sent_count = 0
        self.parse_count = parse_count
        self.lang = lang
        self.corpus = None
        self.sentences = []
        self.ident_map = {}
        self.id_map = {}
        pass

    def add(self, sent):
        """ Add a sentence """
        sent.docID = self.ID
        sent.doc = self
        if sent.ID:
            if sent.ID in self.id_map and self.id_map[sent.ID] is not None:
                getLogger().warning("{}: Duplicate sent ID {}".format(self, sent.ID))
            self.id_map[sent.ID] = sent
        if sent.ident:
            if sent.ident in self.ident_map and self.ident_map[sent.ident] is not None:
                getLogger().warning("{}: Duplicate sent ident {}".format(self, sent.ident))
            self.ident_map[sent.ident] = sent
        self.sentences.append(sent)

    def remove(self, sent):
        if sent and sent in self.sentences:
            if sent.ID in self.id_map:
                self.id_map.pop(sent.ID)
            if sent.ident in self.ident_map:
                self.ident_map.pop(sent.ident)
            self.sentences.remove(sent)
        else:
            raise Exception("Sentence object not found: {}".format(sent))

    def new(self, text='', ident=None):
        sent = Sentence(text=text, ident=ident)
        self.add(sent)
        return sent

    def __repr__(self):
        return "Document(name={})".format(repr(self.name))

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self.sentences)

    def __getitem__(self, idx):
        return self.sentences[idx]

    def __iter__(self):
        return iter(self.sentences)

    def get(self, ID, **kwargs):
        if ID in self.id_map:
            return self.id_map[ID]
        elif 'default' in kwargs:
            return kwargs['default']
        else:
            raise LookupError("Sentence ID#{} could not be found".format(ID))

    def by_ident(self, ident, **kwargs):
        if ident in self.ident_map:
            return self.ident_map[ident]
        elif 'default' in kwargs:
            return kwargs['default']
        else:
            raise LookupError("Sentence ident#{} could not be found".format(ident))

    def to_xml_node(self, corpus_node=None, with_raw=True, with_shallow=True, with_dmrs=True, strict=True):
        doc_node = etree.Element('document')
        if corpus_node is not None:
            corpus_node.append(doc_node)
        doc_node.set('id', str(self.ID) if self.ID else '')
        doc_node.set('name', self.name if self.name else '')
        doc_node.set('title', self.title if self.title else '')
        for sent in self.sentences:
            try:
                sent.to_xml_node(doc_node=doc_node, with_raw=with_raw, with_shallow=with_shallow, with_dmrs=with_dmrs)
            except Exception as e:
                if strict:
                    raise e
                else:
                    logger = getLogger()
                    logger.warning("Sentence {} was corrupted: {}".format(sent.ID, sent.text))
        return doc_node

    def to_xml_str(self, corpus_node=None, pretty_print=True, with_raw=True, with_shallow=True, with_dmrs=True, strict=True):
        xml_node = self.to_xml_node(corpus_node, with_raw, with_shallow, with_dmrs, strict=strict)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    @staticmethod
    def from_xml_node(doc_node, idents=None):
        """ Read sentences from an XML node object """
        logger = getLogger()
        doc = Document(name=get_attr(doc_node, 'name', ''), title=get_attr(doc_node, 'title', ''))
        doc.ident = get_attr(doc_node, 'ident', None)
        doc.ID = get_attr(doc_node, 'ID', None)
        logger.debug("Document: name={} | title={} | ident={} | ID={}".format(doc.name, doc.title, doc.ident, doc.ID))
        sent_nodes = doc_node.findall("sentence")
        getLogger().debug("Found {} sent nodes".format(len(sent_nodes)))
        for sent_node in sent_nodes:
            sent = Sentence.from_xml_node(sent_node)
            if idents and sent.ident not in idents:
                getLogger().debug("Skipped sentence #{}".format(sent.ident))
                continue
            doc.add(sent)
        return doc

    @staticmethod
    def from_xml_str(xml_str, *args, **kwargs):
        doc_root = etree.XML(xml_str, parser=etree.XMLParser(huge_tree=True))
        if doc_root.tag == 'rootisf':
            doc_root = doc_root.find('document')
        return Document.from_xml_node(doc_root, *args, **kwargs)

    @staticmethod
    def from_file(file_path, *args, **kwargs):
        getLogger().info("Reading ISF Document from: {}".format(file_path))
        doc_str = read_file(file_path)
        getLogger().debug("Raw doc string size: {}".format(len(doc_str)))
        doc = Document.from_xml_str(doc_str, *args, **kwargs)
        getLogger().debug("Doc size: {}".format(len(doc)))
        return doc


class Sentence(object):

    NONE = 0
    GOLD = 1
    ERROR = 2
    WARNING = 3

    def __init__(self, text='', ID=None, ident=None, docID=None, doc=None, readings=None):
        # corpus management
        self.ID = ID if ID else None
        self.ident = ident
        self.filename = None
        self.docID = docID
        self.doc = doc
        self.corpus = None
        self.collection = None
        # sentence information
        self.text = StringTool.strip(text)
        self.readings = [] if not readings else list(readings)
        # human annotation layer
        self.flag = None
        self._shallow = None
        self.comment = None
        self.words = []
        self.concepts = []
        self.cmap = {}
        self.wmap = {}

    @property
    def shallow(self):
        if self._shallow:
            return self._shallow
        elif not self.words:
            return None
        else:
            tsent = ttl.Sentence(self.text)
            for word in self.words:
                tk = tsent.new_token(word.word, word.cfrom, word.cto)
                if word.lemma:
                    tk.lemma = word.lemma
                if word.pos:
                    tk.pos = word.pos
                if word.comment:
                    tk.comment = word.comment
            for concept in self.concepts:
                token_ids = [self.words.index(w) for w in concept.words]
                c = tsent.new_concept(concept.tag, concept.clemma, tokens=token_ids)
                if concept.flag:
                    c.flag = concept.flag
                if concept.comment:
                    c.comment = concept.comment
                pass
            return tsent
        pass

    @shallow.setter
    def shallow(self, tagged_sent):
        """ Import a TTL sentence as human annotations """
        self._shallow = tagged_sent
        # add words
        word_map = {}
        for idx, w in enumerate(tagged_sent):
            wobj = Word(widx=idx, word=w.text, lemma=w.lemma, pos=w.pos, cfrom=w.cfrom, cto=w.cto, sent=self)
            if w.comment:
                wobj.comment = w.comment
            word_map[w] = wobj
            self.words.append(wobj)
        # add concepts
        for idx, c in enumerate(tagged_sent.concepts):
            cobj = Concept(cidx=idx, clemma=c.clemma, tag=c.tag, sent=self)
            cobj.comment = c.comment if c.comment else ''
            cobj.flag = c.flag if c.flag else ''
            self.concepts.append(cobj)
            # add cwlinks
            for t in c.tokens:
                tobj = word_map[t]
                cobj.words.append(tobj)

    def is_gold(self):
        return self.flag == Sentence.GOLD

    def is_tagged(self):
        return self.flag in (Sentence.GOLD, Sentence.ERROR, Sentence.WARNING)

    def is_error(self):
        return self.flag == Sentence.ERROR

    def is_warning(self):
        return self.flag == Sentence.WARNING

    def add(self, mrs_str=None, dmrs_xml=None, dmrs_str=None):
        """ Add a new reading to this sentence """
        r = Reading(mrs_str, dmrs_xml, self)
        if dmrs_str is not None:
            j = parse_dmrs_str(dmrs_str)
            if r.dmrs() is None:
                r._dmrs = DMRS(reading=r)
            r.dmrs().from_json(j)
        self.readings.append(r)
        return r

    def __getitem__(self, key):
        """ Get a reading by index """
        return self.readings[key]

    def __len__(self):
        """ Total readings """
        return len(self.readings)

    def __iter__(self):
        return iter(self.readings)

    def __repr__(self):
        return "%s (%s mrs(es))" % (self.text, len(self))

    def __str__(self):
        col = self.collection.name if self.collection else ''
        cor = self.corpus.name if self.corpus else ''
        did = self.docID if self.docID else self.doc.name if self.doc else ''
        sid = "#{}".format(self.ID) if self.ID else ''
        ident = "({})".format(self.ident) if self.ident else ''
        path = "/".join(str(c) for c in (col, cor, did, sid) if c)
        return "{p}{ident}:`{t}` (len={l})".format(p=path, ident=ident, t=self.text, l=len(self))

    def edit(self, key):
        return self[key].edit()

    def tag(self, method=None, **kwargs):
        for parse in self:
            parse.dmrs().tag(method=method, **kwargs)
        return self

    def tag_xml(self, method=None, update_back=True, **kwargs):
        for parse in self:
            parse.dmrs().tag_xml(method=method, update_back=update_back, **kwargs)
        return self

    def to_xml_node(self, doc_node=None, with_raw=True, with_shallow=True, with_dmrs=True, pretty_print=True):
        sent_node = etree.Element('sentence')
        sent_node.set('id', str(self.ID) if self.ID else '')
        sent_node.set('ident', str(self.ident) if self.ident else '')
        sent_node.set('version', '0.1')
        sent_node.set('lang', 'eng')
        # add to doc_node if available
        if doc_node is not None:
            doc_node.append(sent_node)
        # store flag
        if self.flag is not None:
            sent_node.set('flag', str(self.flag))
        # Add license information
        text_node = etree.SubElement(sent_node, 'text')
        text_node.text = self.text
        # store comment
        if self.comment is not None:
            comment_node = etree.SubElement(sent_node, 'comment')
            comment_node.text = etree.CDATA(self.comment)
        # store shallow if needed
        if with_shallow and self.shallow is not None:
            shallow_node = etree.SubElement(sent_node, 'shallow')
            shallow_node.text = json.dumps(self.shallow.to_json(), ensure_ascii=False, indent=2 if pretty_print else None)
        # store readings
        for idx, reading in enumerate(self):
            intp_node = etree.SubElement(sent_node, 'reading')
            intp_node.set('id', str(idx + 1))
            intp_node.set('mode', 'active' if idx == 0 else 'inactive')
            # store MRS (raw)
            if reading.mrs():
                mrs_node = etree.SubElement(intp_node, 'mrs')
                mrs_node.text = etree.CDATA(reading.mrs().tostring(pretty_print=pretty_print))
            # store DMRS
            if with_dmrs and reading.dmrs():
                intp_node.append(reading.dmrs().xml())
        return sent_node

    def to_xml_str(self, pretty_print=True, **kwargs):
        xml_node = self.to_xml_node(pretty_print=pretty_print, **kwargs)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    def to_latex(self):
        return dmrs_tikz_dependency([p.dmrs().obj() for p in self])

    @staticmethod
    def from_xml_node(sent_node):
        sid = sent_node.attrib['id']
        sident = get_attr(sent_node.attrib, 'ident', None)
        text = sent_node.find('text').text
        sentence = Sentence(ID=sid, ident=sident, text=text)
        flag = get_attr(sent_node.attrib, 'flag', None)
        sentence.flag = int(flag) if flag else None
        comment_tag = sent_node.find('comment')
        if comment_tag is not None:
            sentence.comment = comment_tag.text
        shallow_tag = sent_node.find('shallow')
        if shallow_tag is not None and shallow_tag.text:
            shallow = ttl.Sentence.from_json(json.loads(shallow_tag.text))
            sentence.shallow = shallow  # import tags
            for c in shallow.concepts:
                if c.flag == 'E' and sentence.flag is None:
                    sentence.flag = Sentence.ERROR
        for idx, reading_node in enumerate(sent_node.findall('reading')):
            mrs = reading_node.findall('mrs')
            dmrs = reading_node.findall('dmrs')
            if len(mrs) or len(dmrs):
                reading = sentence.add()
                reading.rid = reading_node.attrib['id']
                reading.mode = reading_node.attrib['mode']
            if mrs:
                reading.mrs(mrs[0].text)
            if dmrs:
                reading._dmrs = DMRS()
                reading.dmrs().from_xml_node(dmrs[0])
        return sentence

    @staticmethod
    def from_xml_str(xmlstr):
        return Sentence.from_xml_node(etree.XML(xmlstr))

    @staticmethod
    def from_file(path):
        if path.endswith('.gz'):
            with gzip.open(path, 'rt', encoding='utf-8') as infile:
                return Sentence.from_xml_str(infile.read())
        else:
            with codecs.open(path, encoding='utf-8') as infile:
                return Sentence.from_xml_str(infile.read())


class Reading(object):

    INACTIVE = 0
    ACTIVE = 1

    def __init__(self, mrs_raw=None, dmrs_raw=None, sent=None, ID=None):
        # corpus management
        self.ID = ID
        self.rid = None  # ident?
        self.mode = None  # INACTIVE/ACTIVE
        self.sentID = None
        self.sent = sent
        # reading information
        self._mrs = None  # These should never be accessed directly
        if mrs_raw is not None and len(mrs_raw) > 0:
            self.mrs(mrs_raw)
        self._dmrs = None
        if dmrs_raw is not None and len(dmrs_raw) > 0:
            self.dmrs(dmrs_raw)
        # annotation
        self.comment = None

    def update_mrs(self):
        # Generate MRS from DMRS
        if self._dmrs is not None:
            self._mrs = self.dmrs().to_mrs()

    def update_dmrs(self, with_raw=False):
        # Generate DMRS from MRS
        if self._mrs:
            self._dmrs = self.mrs().to_dmrs(with_raw=with_raw)

    def mrs(self, mrs_raw=None):
        if mrs_raw is not None:
            self._mrs = MRS(mrs_raw, self)
        if self._mrs is None:
            self.update_mrs()
        return self._mrs

    def dmrs(self, dmrs_raw=None):
        if dmrs_raw is not None:
            self._dmrs = DMRS(dmrs_raw, self)
        if self._dmrs is None:
            self.update_dmrs()
        return self._dmrs

    def edit(self):
        return self.dmrs().edit()

    def __repr__(self):
        return "Reading(ID={rid}, mode={mode})".format(rid=self.rid, mode=self.mode)

    def __str__(self):
        return str(self.mrs().tostring(False))


class MRS(object):

    def __init__(self, mrs_raw, reading=None):
        # corpus management
        self.ID = None
        self.ident = None
        self.readingID = reading.ID if reading is not None else None
        # data
        self._raw = mrs_raw
        self._obj = None
        self.reading = reading

    @property
    def raw(self):
        return self._raw

    def obj(self):
        """ Get pydelphin MRS object
        """
        if self._obj is None:
            self._obj = simplemrs.loads_one(self._raw)
        return self._obj

    # ---------------------
    # Interchange formats
    # ---------------------
    def json(self):
        return Mrs.to_dict(self.obj(), properties=True)

    def json_str(self):
        """MRS data in JSON format"""
        return json.dumps(self.json(), ensure_ascii=False)

    def to_dmrs(self, with_raw=False):
        xml_str = dmrx.dumps_one(self.obj())
        dmrs_node = etree.XML(xml_str)[0]
        # insert RAW to dmrs_xml
        if with_raw:
            raw_node = etree.Element('raw')
            raw_node.text = etree.CDATA(self.tostring())
            dmrs_node.insert(0, raw_node)
        return DMRS(etree.tostring(dmrs_node).decode('utf-8'), reading=self.reading)

    def tostring(self, pretty_print=True):
        """prettified MRS string"""
        return simplemrs.dumps_one(self.obj(), pretty_print=pretty_print)

    def __str__(self):
        return self.tostring()


SenseTag = namedtuple("SenseTag", ("synset", "method"))


class DMRS(object):

    def __init__(self, dmrs_xml=None, reading=None, tags=None):
        # Corpus management
        self.ID = None
        self.ident = None
        self.readingID = reading.ID if reading is not None else None
        self.reading = reading
        # DMRS information
        self.cfrom = -1
        self.cto = -1
        self.surface = None
        # Internal properties, should NOT be accessed directly
        self._raw = dmrs_xml  # only support DMRS XML format for now
        self._layout = None  # editable DMRS
        self._obj = None  # pydelphin object
        self._node = None  # xml_node cache
        self.tags = dd(list)  # sense tagging
        if tags:
            self.tags.update(tags)
        # find tags in XML if available
        if self._raw is not None:
            self.find_tags()
        self.tagged = set()

    @property
    def raw(self):
        return self._raw

    @raw.setter
    def raw(self, value):
        self.reset(raw=value)

    @property
    def layout(self):
        if self._layout is None:
            self._layout = self.edit()
        return self._layout

    def reset(self, raw=None, layout=None, obj=None, node=None, tags=None):
        # This should ONLY be used in case of changing internal layout
        self._raw = raw
        self._layout = layout
        self._obj = obj
        self._node = node
        self.tags = dd(list)
        if tags is not None:
            self.tags.update(tags)

    def from_xml_node(self, xml_node):
        self.reset(node=xml_node)
        self._node = xml_node
        self._raw = etree.tostring(xml_node).decode('utf-8')
        self.find_tags()
        if self.reading:
            self.reading.update_mrs()

    def from_json(self, j):
        self.reset(obj=Dmrs.from_dict(j))
        if self.reading is not None:
            self.reading.update_mrs()
        return self

    def surface(self, node):
        if node is None or self.parse is None or self.reading.sent is None:
            return None
        else:
            return self.reading.sent.text[int(node.cfrom):int(node.cto)]

    def preds(self):
        """ Get all pred strings """
        return [normalize_pred_string(x.pred.string) for x in self.obj().eps()]

    def clear(self):
        self._obj = None
        self._node = None

    # ----------------------------
    # Support different formats
    # ----------------------------

    def xml(self):
        if self._node is None:
            # reparse DMRS node
            # should tag be re-inserted here?
            if self._raw is not None:
                # from raw XML string?
                self._node = etree.XML(self._raw)
            else:
                if self._obj is None:
                    if self.layout:
                        self.layout.save()
                    else:
                        raise Exception("Broken DMRS object")
                # from pyDelphin object?
                xml_str = dmrx.dumps_one(self._obj)
                dmrs_list_node = etree.XML(xml_str)
                self._raw = None
                self._node = dmrs_list_node[0]
        return self._node

    def xml_str(self, pretty_print=False):
        if self._raw is not None and not pretty_print:
            return self._raw
        return etree.tostring(self.xml(), pretty_print=pretty_print).decode('utf-8')

    def latex(self):
        return dmrs_tikz_dependency(self.obj())

    def json(self):
        j = Dmrs.to_dict(self.obj(), properties=True)
        # sense-tagging if possible
        # JSON will be tagged with mfs by default
        # [2017-07-26] Don't tag JSON by default, it's slow
        tags = self.tags if self.tags else self.tag(method=ttl.Tag.DEFAULT)
        # getLogger().debug("Tagging JSON with {}".format(tags))
        for node in j['nodes']:
            nid = node['nodeid']
            if nid in tags and len(tags[nid]) > 0:
                node['senses'] = []
                # sort by WSD method
                tags[nid].sort(key=lambda x: 1 if x[1] == ttl.Tag.GOLD else 10 if x[1] == ttl.Tag.LELESK else 50 if ttl.Tag.MFS else 100)
                for tag, tagtype in tags[nid]:
                    node['senses'].append({'synsetid': str(tag.synsetid), 'lemma': tag.lemma, 'type': tagtype})
        # These are for visko
        # add sentence text if it's available
        if self.reading is not None and self.reading.sent is not None:
            j['text'] = self.reading.sent.text
        # Add pred type and pos
        for node, ep in zip(j['nodes'], self.obj().eps()):
            node['type'] = 'gpred' if (ep.pred.type == Pred.GRAMMARPRED) else 'realpred'
            if ep.pred.pos:
                node['pos'] = ep.pred.pos
        # Remove empty rargname
        for link in j['links']:
            if link['rargname'] is None:
                link['rargname'] == ''
        return j

    def json_str(self):
        """DMRS data in JSON format"""
        try:
            return json.dumps(self.json(), ensure_ascii=False)
        except:
            return None

    def obj(self):
        """ Get pydelphin DMRS object
        """
        if self._obj is None:
            xml_str = '<dmrs-list>{}</dmrs-list>'.format(self.xml_str())
            mrses = []
            try:
                mrses.extend(dmrx.loads(xml_str))
            except:
                getLogger().exception("Error occurred while deserializing this DMRS {}".format(xml_str))
                raise
            if len(mrses) == 1:
                self._obj = mrses[0]
                # store available tags
                self.find_tags()
            else:
                raise Exception("Could not deserialize DMRS object")
        return self._obj

    def to_mrs(self):
        mrs_str = simplemrs.dumps_one(self.obj())
        return MRS(mrs_str, reading=self.reading)

    def tostring(self, pretty_print=True):
        """prettified DMRS string"""
        return simpledmrs.dumps_one(self.obj(), pretty_print=pretty_print)

    def __str__(self):
        return self.tostring()

    # -------------------------------
    # Read & write tags from/to XML
    # -------------------------------

    def find_tags(self):
        """ Find all available sense tags that are stored in XML"""
        root = self.xml()
        if root is not None:
            tags = dd(list)
            nodes = root.findall('./node')
            for n in nodes:
                # find all sense nodes
                carg = n.attrib['carg'] if 'carg' in n.attrib else ''
                sense_nodes = n.findall('sense')
                if sense_nodes is None:
                    sense_nodes = []
                sg = n.find('sensegold')
                if sg is not None:
                    sense_nodes.append(sg)
                    sg.attrib['method'] = ttl.Tag.GOLD
                for s in sense_nodes:
                    nodeid = int(n.attrib['nodeid'])
                    sid = s.attrib['synsetid']
                    lemma = s.attrib['lemma']
                    score = s.attrib['score'] if 'score' in s.attrib else None
                    method = s.attrib['type'] if 'type' in s.attrib else ttl.Tag.ISF
                    self.tag_node(nodeid, sid, carg or lemma, method, score=score)
            # end for
            # tag list is stored esp for JSON
            if tags:
                for k, new_tags in tags.items():
                    for new_tag in new_tags:
                        if new_tag not in self.tags[k]:
                            self.tags[k].append(new_tag)
        return self.tags

    def tag(self, method=ttl.Tag.MFS, wsd=None, strict=False, ctx=None):
        """ Sense tag this DMRS using a WSD method (by default is most-frequent sense)
        and then return a map from nodeid to a list of tuples in this format (Synset, sensetype=str)
        """
        if method not in (ttl.Tag.LELESK, ttl.Tag.MFS):
            return {}  # no tag
        if wsd is None:
            wsd = LeLeskWSD(dbcache=LeskCache())
            if ctx is None:
                with PredSense.wn.ctx() as ctx:
                    getLogger().warning("Creating a new WSD, this can be optimized further ...")
                    return self.tag(method=method, wsd=wsd, strict=strict, ctx=ctx)
        eps = self.get_lexical_preds(strict=strict)
        getLogger().debug("eps for WSD: {}".format(eps))
        context = self.get_wsd_context()  # all lemmas from other predicates
        for ep in eps:
            # taggable eps
            # TODO: Use POS for better sense-tagging?
            getLogger().debug("processing {}".format(ep))
            # getLogger().debug("Performing WSD using {} on {}({})/{}".format(method, lemma, ep.pred.lemma, context))
            candidates = PredSense.search_ep(ep, ctx=ctx)
            if not candidates:
                # getLogger().debug("No candidate was found for {}".format(ep.pred.string))
                continue
            lemma = get_ep_lemma(ep)
            scores = []
            if method == ttl.Tag.LELESK:
                scores = wsd.lelesk_wsd(lemma, '', lemmatizing=False, context=context, synsets=candidates)
            elif method == ttl.Tag.MFS:
                scores = wsd.mfs_wsd(lemma, '', lemmatizing=False, synsets=candidates)
            if scores:
                # insert the top one
                best = scores[0].candidate.synset
                getLogger().debug("Lemma: {} -> {} | {}".format(lemma, scores[0].candidate.synset.lemmas, scores[0]))
                self.tag_node(ep.nodeid, best.synsetid, best.lemma, method)
            else:
                # What should be done here? no tagging at all?
                pass
        self.tagged.add(method)
        return self.tags

    def tag_xml(self, method=ttl.Tag.MFS, update_back=False, **kwargs):
        """ Generate an XML object with available tags
        (perform provided sense-tagging method if required) """
        # Sense-tagging only if required
        if method is None or method in self.tagged:
            # 1 method will only be performed once
            tags = self.tags
        else:
            tags = self.tag(method, **kwargs)
        root = self.xml()
        for node in root.findall('node'):
            # remove previous tags
            for child in itertools.chain(node.findall('sense'), node.findall('sensegold')):
                node.remove(child)
            if int(node.get('nodeid')) in tags:
                ntags = tags[int(node.get('nodeid'))]
                for ntag in ntags:
                    if ntag.method == ttl.Tag.GOLD:
                        gold_node = etree.SubElement(node, 'sensegold')
                        gold_node.set('synsetid', str(ntag.synset.synsetid))
                        gold_node.set('lemma', ntag.synset.lemma)
                        gold_node.set('type', ntag.method)
                    elif ntag.method:
                        candidate_node = etree.SubElement(node, 'sense')
                        candidate_node.set('synsetid', str(ntag.synset.ID))  # [2015-10-26] FCB: synsetid format should be = 12345678-x]
                        candidate_node.set('lemma', str(ntag.synset.lemma))
                        candidate_node.set('score', str(ntag.synset.tagcount))
                        candidate_node.set('type', ntag.method)
                    else:
                        # DEFAULT? etc.
                        # Do nothing for now
                        pass
        # update self.xml?
        if update_back:
            self.reset(node=root, tags=tags)
        return root

    # -------------------------------
    # Sense-tagging
    # -------------------------------

    def tag_node(self, nodeid, synsetid, lemma, method, score=None):
        synset = Synset(synsetid, lemma=lemma)
        if score:
            synset.tagcount = score
        sensetag = SenseTag(synset, method)
        if sensetag not in self.tags[nodeid]:
            # getLogger().debug("Tagging {} with {} - current: {}".format(nodeid, sensetag, self.tags[nodeid]))
            self.tags[nodeid].append(sensetag)

    def get_wsd_context(self):
        """ All lemmas from predicates """
        return (get_ep_lemma(p) for p in self.get_lexical_preds())

    def is_known_gpred(self, pred):
        return pred in ("named_rel", 'superl_rel', '_be_v_id_rel')

    def get_lexical_preds(self, strict=False):
        preds = []
        for p in self.obj().eps():
            pred_str = str(p.pred)
            if not pred_str.endswith('_rel'):
                pred_str += '_rel'
            if pred_str in ('named_rel', 'unknown_rel'):
                # ALWAYS ignore named_rel
                continue
            if strict and p.pred.type not in (Pred.REALPRED, Pred.STRINGPRED) and not self.is_known_gpred(pred_str) and not p.carg:
                # [WIP] if can get CARG, count on it!
                continue
            preds.append(p)
        return preds

    def tokenize_pos(self, strict=False):
        """ Convert a DMRS to a token list with POS """
        token_list = []
        for ep in self.get_lexical_preds(strict=strict):
            pos = PredSense.get_wn_pos(ep)
            token_list.append((get_ep_lemma(ep), pos, ep.cfrom, ep.cto))
        # TODO: lemma or surface form?
        # ignore some grammatical preds?
        return token_list

    def edit(self):
        return DMRSLayout(self.json(), self)


def get_attr(a_dict, key, default):
    return a_dict[key] if key in a_dict else default


class Predicate(object):

    GRAMMARPRED = Pred.GRAMMARPRED
    REALPRED = Pred.REALPRED
    STRINGPRED = Pred.STRINGPRED
    VALID_TYPES = {GRAMMARPRED, REALPRED, STRINGPRED}

    def __init__(self, ptype, lemma, pos=None, sense=None):
        """

        """
        if ptype not in Predicate.VALID_TYPES:
            raise Exception("Invalid pred type")
        self._ptype = ptype
        self._lemma = lemma
        self._pos = pos
        self._sense = sense
        self._predstr = None

    @staticmethod
    def from_string(predstr):
        if predstr:
            p = Pred.string_or_grammar_pred(predstr)
            return Predicate(p.type, p.lemma, p.pos, p.sense)
        else:
            return None

    @property
    def ptype(self):
        return self._ptype

    @ptype.setter
    def ptype(self, value):
        self._predstr = None
        self._ptype = value

    @property
    def lemma(self):
        return self._lemma

    @lemma.setter
    def lemma(self, value):
        self._predstr = None
        self._lemma = value

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._predstr = None
        self._pos = value

    @property
    def sense(self):
        return self._sense

    @sense.setter
    def sense(self, value):
        self._predstr = None
        self._sense = value

    @property
    def predstr(self):
        if self._predstr is None:
            if self.ptype == self.REALPRED or self.ptype == self.STRINGPRED:
                self._predstr = '_'.join([x for x in ('', self.lemma, self.pos, self.sense) if x is not None])
            else:
                self._predstr = '_'.join([x for x in (self.lemma, self.pos, self.sense) if x is not None])
        return self._predstr

    def to_pred(self):
        return Pred.string_or_grammar_pred(self.predstr)

    def __str__(self):
        return self.to_pred().short_form()


Triplet = namedtuple("Triplet", ("name", "in_links", "out_links"))


class Node(object):

    def __init__(self, nodeid=None, predstr=None, cfrom=-1, cto=-1, sortinfo=None, pos=None, surface=None, base=None, carg=None, predtype=None, dmrs=None):
        # corpus management
        self.ID = None
        self.dmrsID = None
        # node information
        self.nodeid = int(nodeid) if nodeid is not None else None
        self._pred = None
        self.cfrom = int(cfrom) if cfrom is not None else -1
        self.cto = int(cto) if cto is not None else -1
        self.sortinfo = sortinfo if sortinfo else SortInfo()
        if sortinfo is not None:
            sortinfo.nodeID = self.ID
        self.surface = surface
        self.base = base
        self.carg = carg
        self.links = LinkMap()
        self.dmrs = dmrs
        # gpred
        self.gpred_valueID = None
        # realpred
        self.rplemmaID = None
        # annotation
        self.sense = None
        self.synsetid = None
        self.synset_score = None
        # init pred string
        if predstr is not None:
            self.pred = predstr

    @property
    def predtype(self):
        if self.pred is None:
            return ''
        elif self.pred.ptype == Predicate.GRAMMARPRED:
            return 'gpred'
        else:
            return 'realpred'

    @property
    def pred(self):
        return self._pred

    @pred.setter
    def pred(self, value):
        if isinstance(value, Predicate):
            self._pred = value
        else:
            self._pred = Predicate.from_string(value)

    @property
    def predstr(self):
        return str(self.pred)

    @property
    def rplemma(self):
        if self.pred is None or self.pred.ptype == Predicate.GRAMMARPRED:
            return None
        else:
            return self.pred.lemma

    @rplemma.setter
    def rplemma(self, value):
        if self._pred is None:
            self._pred = Predicate(Predicate.REALPRED, value)
        else:
            self.pred.lemma = value

    @property
    def rppos(self):
        if self.pred is None or self.pred.ptype == Predicate.GRAMMARPRED:
            return None
        else:
            return self.pred.pos

    @rppos.setter
    def rppos(self, value):
        if self._pred is None:
            self._pred = Predicate(Predicate.REALPRED, '', pos=value)
        else:
            self.pred.pos = value

    @property
    def rpsense(self):
        if self.pred is None or self.pred.ptype == Predicate.GRAMMARPRED:
            return None
        else:
            return self.pred.sense

    @rpsense.setter
    def rpsense(self, value):
        if self._pred is None:
            self._pred = Predicate(Predicate.REALPRED, '', sense=value)
        else:
            self.pred.sense = value

    @property
    def gpred(self):
        if self.pred is not None and self.pred.ptype == Predicate.GRAMMARPRED:
            return self.predstr
        else:
            return None

    @property
    def out_links(self):
        return self.links.out_links

    @property
    def in_links(self):
        return self.links.in_links

    def arg(self, name):
        return self.links.out_map[name] if name in self.links.out_map else None

    def __getitem__(self, name):
        return self.arg(name)

    def to_graph(self, top=None, visited=None, scan_outlinks=False):
        if top is None:
            top = self
        if visited is None:
            visited = set()
        visited.add(self)
        in_links = frozenset((l.label, l.from_node.to_graph(top, visited)) for l in self.in_links if l.from_node is not None and l.from_node not in visited)
        if not scan_outlinks and self == top:
            out_links = None
        else:
            out_links = frozenset((l.label, l.to_node.to_graph(top, visited)) for l in self.out_links if l.to_node is not None and l.to_node not in visited)
        # need to match carg too
        return Triplet((self.predstr, self.carg), in_links, out_links)

    def rstr(self):
        return [l.from_node for l in self.in_links if l.rargname == 'RSTR' and l.post == 'H']

    def to_json(self):
        a_dict = {'nodeid': int(self.nodeid),
                  'predicate': str(self.pred),
                  'lnk': {'from': int(self.cfrom), 'to': int(self.cto)},
                  'sortinfo': self.sortinfo.to_json()}
        if self.surface:
            a_dict['surface'] = self.surface
        if self.base:
            a_dict['base'] = self.base
        if self.carg:
            a_dict['carg'] = self.carg
        return a_dict

    @staticmethod
    def from_json(j):
        return Node(j['nodeid'],
                    j['predicate'],
                    j['lnk']['from'],
                    j['lnk']['to'],
                    SortInfo.from_json(get_attr(j, 'sortinfo', {})),
                    get_attr(j, 'pos', None),
                    get_attr(j, 'surface', None),
                    get_attr(j, 'base', None),
                    get_attr(j, 'carg', None),
                    get_attr(j, 'predtype', None))

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{} [{}<{}:{}>]".format(self.nodeid, self.pred, self.cfrom, self.cto)

    def is_unk(self):
        return self.predstr == 'unknown'

    def is_comp(self):
        return self.predstr == 'compound'

    def is_udef(self):
        return self.predstr == 'udef_q'

    def to_string(self):
        """ node to parsable string format """
        if self.gpred:
            pred = self.gpred
        else:
            pred = Pred.realpred(self.rplemma, self.rppos, self.rpsense if self.rpsense else None).short_form()
        sensetag = ''
        if self.sense:
            sensetag = ' synsetid={} synset_lemma={} synset_score={}'.format(self.sense.synsetid, self.sense.lemma.replace(' ', '+'), self.sense.score)
        carg = '("{}")'.format(self.carg) if self.carg else ''
        return "{nodeid} [{pred}<{cfrom}:{cto}>{carg} {sortinfo}{sensetag}]".format(nodeid=self.nodeid, cfrom=self.cfrom, cto=self.cto, sortinfo=self.sortinfo.to_string(), sensetag=sensetag, pred=pred, carg=carg)


class GpredValue(object):
    """
    Gpred (grammar predicate) value
    """
    def __init__(self, value=None):
        self.ID = None
        self.value = value

    def __str__(self):
        return "#{}({})".format(self.ID, self.value)


class Sense(object):
    def __init__(self, lemma='', pos='', synsetid='', score=0):
        self.lemma = lemma
        self.pos = pos
        self.synsetid = synsetid
        self.score = score


class Lemma(object):
    """
    Lemma of Real pred
    """
    def __init__(self, lemma=None):
        self.ID = None
        self.lemma = lemma

    def __str__(self):
        return "#{}({})".format(self.ID, self.lemma)


class Link(object):

    def __init__(self, from_node=0, to_node=0, rargname=None, post=None, dmrs=None):
        # corpus management
        self.ID = None
        self.dmrsID = None
        # link information
        self.from_nodeid = int(from_node)
        self.to_nodeid = int(to_node)
        self.rargname = rargname
        self.post = post
        self.dmrs = dmrs

    def to_json(self):
        return {
            'from': self.from_nodeid,
            'to': self.to_nodeid,
            'rargname': self.rargname,
            'post': self.post
        }

    @property
    def from_node(self):
        return self.dmrs[self.from_nodeid] if self.dmrs else None

    @property
    def to_node(self):
        return self.dmrs[self.to_nodeid] if self.dmrs else None

    @property
    def label(self):
        return "{}/{}".format(self.rargname if self.rargname else '', self.post if self.post else '')

    def is_rstr(self):
        return self.rargname == 'RSTR' and self.post == 'H'

    @staticmethod
    def from_json(json):
        return Link(from_node=json['from'],
                    to_node=json['to'],
                    rargname=json['rargname'],
                    post=json['post'])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return "{}:{}/{} -> {}".format(self.from_nodeid, self.rargname, self.post, self.to_nodeid)


class LinkMap(object):

    def __init__(self):
        self.in_links = list()
        self.out_links = list()
        self.out_map = {}

    def link_in(self, lnk):
        self.in_links.append(lnk)

    def unlink_in(self, lnk):
        self.in_links.remove(lnk)

    def link_out(self, lnk):
        self.out_links.append(lnk)
        self.out_map[lnk.rargname] = lnk.to_node

    def unlink_out(self, lnk):
        self.out_links.remove(lnk)
        self.pop(lnk.rargname)


class DMRSLayout(object):

    def __init__(self, data=None, source=None):
        # corpus management
        self.ID = None
        self.ident = None
        self.readingID = None
        # information
        self.cfrom = None
        self.cto = None
        self.surface = None
        self._nodes = []
        self._links = []
        self._node_map = {}
        self._top = None  # point to a Node object or None
        self._tags = dd(set)  # map nodeid => a list of (SynsetID(sid, lemma), method)
        if data is not None:  # JSON data
            for node in data['nodes']:
                nobj = Node.from_json(node)
                self.add_node(nobj)
                if 'sense' in node:
                    sense = node['sense']
                    synset = Synset(sense['synsetid'], lemma=sense['lemma'])
                    self._tags[nobj.nodeid].add((synset, ttl.Tag.OTHER))
                    # TODO: proper tagging method and score?
            for link in data['links']:
                self.add_link(Link.from_json(link))
        self.source = source  # DMRS object

    @property
    def top(self):
        return self._top

    def head(self):
        if self.top is None:
            return None
        elif self.top.predstr == "unknown" and self.top['ARG'] is not None:
            return self.top["ARG"]
        else:
            return self.top

    @property
    def to_string(self):
        """ To parsable string format (human friendly)"""
        nodes = [n.to_string() for n in self.nodes if str(n.nodeid) != '0']
        links = [l.to_string() for l in self.links]
        return "dmrs {{\n{nl}\n}} ".format(ident=self.ident, cfrom=self.cfrom, to=self.cto, surface=self.surface, nl=';\n'.join(nodes + links))

    @top.setter
    def top(self, value):
        if value in self:
            self._top = self[value]
        elif value in self._nodes:
            self._top = value
        else:
            raise Exception("Invalid node object invaded ({}({}) was provided)".format(repr(value), type(value)))

    def __getitem__(self, nodeid):
        return self._node_map[nodeid] if nodeid in self._node_map else None

    def __contains__(self, nodeid):
        return nodeid in self._node_map

    def add_node(self, node):
        node.dmrs = self
        self._nodes.append(node)
        self._node_map[node.nodeid] = node

    def add_link(self, link):
        link.dmrs = self
        self._links.append(link)
        if link.from_nodeid == 0:
            # FOUND TOP
            self.top = link.to_nodeid
        else:
            self[link.from_nodeid].links.link_out(link)
        self[link.to_nodeid].links.link_in(link)

    def delete_link(self, link):
        if link.from_nodeid in self:
            self[link.from_nodeid].links.out_links.remove(link)
        if link.to_nodeid in self:
            self[link.to_nodeid].links.in_links.remove(link)
        if link in self._links:
            self._links.remove(link)

    def delete_node(self, nodeid):
        node = self[nodeid]
        if node is None:
            return
        # delete all links
        self.delete(*node.out_links)
        self.delete(*node.in_links)
        # delete node
        if node == self.top:
            self._top = None
        self._nodes.remove(node)
        self._node_map.pop(node.nodeid)

    def delete(self, *items):
        for item in items:
            if isinstance(item, Node):
                # Delete a node
                self.delete_node(item.nodeid)
            elif isinstance(item, Link):
                # Delete a link
                self.delete_link(item)
            elif isinstance(item, DMRSLayout):
                # delete a subgraph
                self.delete_sub(item)
            else:
                # delete a node by id
                self.delete_node(item)
        return self

    def delete_sub(self, sub):
        """ Delete a subgraph except its head"""
        sub_head = self[sub.top.nodeid]
        sub_nodes = [n for n in sub.nodes if sub_head and n.nodeid != sub_head.nodeid]
        self.delete(*sub_nodes)

    def adjacent_nodes(self):
        """ Generate a set of preds that are adjacent """
        adj_list = dd(list)
        for n in self.nodes:
            # ignore RSTR
            if n.is_unk() or (not n.in_links and len(n.out_links) == 1 and n.out_links[0].is_rstr()):
                continue
            adj_list[n.cfrom].append(n)
            adj_list[n.cto + 1].append(n)
            adj_list[n.cto].append(n)
        getLogger().debug("adjacent dict: {}".format(adj_list))
        return {frozenset(n.predstr for n in v) for k, v in adj_list.items() if len(v) > 1}

    def subgraph(self, headid, constraints=None, ignore_rstr=True):
        if isinstance(headid, Node):
            headid = headid.nodeid
        if isinstance(constraints, DMRSLayout):
            constraints = [n.predstr for n in constraints.nodes]
        head = self[headid]
        head_rstr = [r.nodeid for r in head.rstr()]
        nodeids = set()
        sub = DMRSLayout()
        candidates = [l.from_nodeid for l in head.in_links]
        links = set(l for l in head.in_links)
        while candidates:
            c = candidates.pop()
            if ignore_rstr and c in head_rstr:
                continue
            if c != headid and c not in nodeids and c in self:
                if constraints is not None:
                    if self[c].predstr not in constraints:
                        continue
                nodeids.add(c)
                candidates.extend(l.from_nodeid for l in self[c].in_links)
                candidates.extend(l.to_nodeid for l in self[c].out_links)
                links.update(self[c].in_links)
                links.update(self[c].out_links)
        # Add nodes and links to subgraph
        nodeids.add(headid)
        for nodeid in sorted(nodeids):
            new_node = copy.copy(self[nodeid])
            new_node.pred = self[nodeid].predstr
            new_node.links = LinkMap()
            sub.add_node(new_node)
        for link in links:
            if link.from_nodeid in nodeids and link.to_nodeid in nodeids:
                new_link = copy.copy(link)
                sub.add_link(new_link)
        sub.top = sub[headid]
        return sub

    def match(self, other):
        if self.top is None:
            raise Exception("I am not headed")
        else:
            if other.top is None:
                return False
        return False

    @property
    def nodes(self):
        return self._nodes

    @property
    def links(self):
        return self._links

    def preds(self):
        return [n.predstr for n in self.nodes]

    def to_json(self):
        return {'nodes': [n.to_json() for n in self.nodes],
                'links': [l.to_json() for l in self.links],
                'tags': dict(self._tags)}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.to_json())

    def save(self):
        if self.source is not None:
            self.source.from_json(self.to_json())
        return self

    def to_dmrs(self):
        return DMRS().from_json(self.to_json())

    @staticmethod
    def from_xml_str(xml_content):
        root = etree.XML(xml_content)
        if root.tag == "reading":
            root = root.findall("dmrs")[0]
        return DMRSLayout.from_xml(root)

    @staticmethod
    def from_xml(dmrs_tag):
        """ Get DMRS from XML node
        """
        dmrs = DMRSLayout()
        dmrs.ident = get_attr(dmrs_tag.attrib, 'ident', '')
        dmrs.cfrom = get_attr(dmrs_tag.attrib, 'cfrom', '')
        dmrs.cto = get_attr(dmrs_tag.attrib, 'cto', '')
        dmrs.surface = get_attr(dmrs_tag.attrib, 'surface', '')

        # parse all nodes inside
        for node_tag in dmrs_tag.findall('node'):
            nid = int(node_tag.attrib['nodeid'])
            cfrom = int(node_tag.attrib['cfrom'])
            cto = int(node_tag.attrib['cto'])
            surface = get_attr(node_tag.attrib, 'surface', '')
            base = get_attr(node_tag.attrib, 'base', '')
            carg = get_attr(node_tag.attrib, 'carg', '')
            # TODO: parse sort info
            sortinfo_tag = node_tag.find("sortinfo")
            sortinfo = SortInfo().update(sortinfo_tag.attrib) if sortinfo_tag is not None else None
            pred = None
            gpred_tag = node_tag.find("gpred")
            if gpred_tag is not None:
                pred = gpred_tag.text
            else:
                realpred_tag = node_tag.find("realpred")
                if realpred_tag is not None:
                    lemma = get_attr(realpred_tag.attrib, 'lemma', '')
                    pos = get_attr(realpred_tag.attrib, 'pos', '')
                    sense = get_attr(realpred_tag.attrib, 'sense', '')
                    pred = Predicate(Predicate.REALPRED, lemma, pos, sense)
            temp_node = Node(nid, pred, cfrom=cfrom, cto=cto, sortinfo=sortinfo, surface=surface, base=base, carg=carg)

            # Parse sense info
            sensegold_tag = node_tag.find('sensegold')
            if sensegold_tag is not None:
                # if we have sensegold, use it instead
                sense_info = Sense()
                sense_info.lemma = sensegold_tag.attrib['lemma']
                sense_info.synsetid = sensegold_tag.attrib['synsetid']
                sense_info.pos = sense_info.synsetid[-1]
                sense_info.score = '999'
                temp_node.sense = sense_info
                getLogger().debug("Using gold => %s" % (sense_info.synsetid))
                pass
            else:
                sense_tag = node_tag.find('sense')
                if sense_tag is not None:
                    sense_info = Sense()
                    update_obj(sense_tag.attrib, sense_info)
                    temp_node.sense = sense_info

            # Completed parsing, add the node_tag to DMRS object
            dmrs.nodes.append(temp_node)
            # end for nodes

        # parse all links inside
        for link_tag in dmrs_tag.findall('link'):
            fromNodeID = int(link_tag.attrib['from'])
            toNodeID = int(link_tag.attrib['to'])
            # TODO: parse post
            post_tag = link_tag.find("post")
            post = post_tag.text if post_tag is not None else ''
            rargname_tag = link_tag.find("rargname")
            rargname = rargname_tag.text if rargname_tag is not None else ''
            dmrs.links.append(Link(fromNodeID, toNodeID, rargname, post))
        # finished, add dmrs object to reading
        return dmrs


class SortInfo(object):

    KNOWN_FIELDS = {'cvarsort', 'num', 'pers', 'gend', 'sf', 'tense',
                    'mood', 'prontype', 'prog', 'perf', 'ind'}
    ORDER = ['num', 'pers', 'gend', 'sf', 'tense', 'mood', 'prontype', 'prog', 'perf', 'ind']
    PRIVATE = ['ID', 'dmrs_nodeID', 'data']

    """
    sortinfo of a Node
    """
    def __init__(self, cvarsort='', num='', pers='', gend='', sf='', tense='', mood='', prontype='', prog='', perf='', ind='', dmrs_nodeID=None):
        # corpus management
        object.__setattr__(self, "ID", None)
        object.__setattr__(self, "dmrs_nodeID", None)
        object.__setattr__(self, "data", {})
        # known fields
        self.cvarsort = cvarsort
        self.num = num
        self.pers = pers
        self.gend = gend
        self.sf = sf
        self.tense = tense
        self.mood = mood
        self.prontype = prontype
        self.prog = prog
        self.perf = perf
        self.ind = ind

    def __str__(self):
        return self.to_string()

    def __setattr__(self, name, value):

        if name in SortInfo.PRIVATE:
            object.__setattr__(self, name, value)
        else:
            self.data[name] = value

    def __getattr__(self, name):
        if name in SortInfo.PRIVATE:
            return self.__dict__[name]
        if name in self.data:
            return self.data[name]
        else:
            return None

    def update(self, data):
        self.data.update(data)
        return self

    @staticmethod
    def from_json(j):
        si = SortInfo().update(j)
        return si

    def to_json(self):
        j = {k: v for k, v in self.data.items() if v}
        return j

    def to_string(self):
        valdict = [(k, self.data[k]) for k in SortInfo.ORDER if self.data[k]]
        extra = [(k, self.data[k]) for k in sorted(self.data.keys()) if k not in SortInfo.ORDER and k not in SortInfo.PRIVATE and self.data[k]]
        valdict.extend(extra)
        if self.cvarsort:
            return self.cvarsort + ' ' + ' '.join(('{}={}'.format(k.upper(), str(v)) for (k, v) in valdict))
        else:
            return ' '.join(('{}={}'.format(k.upper(), str(v)) for (k, v) in valdict))


class LexUnit(object):

    PROCESSED = 1
    ERROR = 2  # couldn't parse
    GOLD = 3
    COMPOUND = 4  # to be further processed, but most likely are compounds
    MWE = 5  # compound that were confirmed are multi-word expressions
    MISMATCHED = 6  # wrong POS
    UNKNOWN = 7
    NOM_VERB = 8
    COMP_NN = 9  # Noun-noun compound
    COMP_AN = 10  # Adj-noun compound
    COMP_NE = 11  # named-entity
    NOUN = 12     # Nouns in general
    VERB = 13     # Verbs in general
    ADJ = 14     # Adjectives in general
    ADV = 15     # Adverbs in general

    FLAGS = {
        PROCESSED: "LexUnit.PROCESSED",
        ERROR: "LexUnit.ERROR",
        GOLD: "LexUnit.GOLD",
        COMPOUND: "LexUnit.COMPOUND",
        MWE: "LexUnit.MWE",
        MISMATCHED: "LexUnit.MISMATCHED",
        UNKNOWN: "LexUnit.UNKNOWN",
        NOM_VERB: "LexUnit.NOM_VERB",
        COMP_NN: "LexUnit.COMP_NN",
        COMP_AN: "LexUnit.COMP_AN",
        COMP_NE: "LexUnit.COMP_NE",
        NOUN: "LexUnit.NOUN",
        VERB: "LexUnit.VERB",
        ADJ: "LexUnit.ADJ",
        ADV: "LexUnit.ADV"
    }

    def __init__(self, ID=None, lemma=None, pos=None, synsetid=None, sentid=None, flag=None):
        self.ID = None
        self.lemma = lemma
        self.pos = pos
        self.synsetid = synsetid
        self.flag = flag
        self.sentid = sentid
        self.parses = None

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.parses) if self.parses is not None else 0

    def __getitem__(self, idx):
        if self.parses is not None:
            return self.parses[idx]
        return None

    def __str__(self):
        return "LexUnit({}, {}, {}, {}, {}, {})".format(self.ID, repr(self.lemma), repr(self.pos), repr(self.synsetid), repr(self.sentid), LexUnit.FLAGS[self.flag] if self.flag else None)


class RuleInfo(object):

    INACTIVE = 0
    SINGLE_PRED = 1
    COMPOUND = 2

    def __init__(self, ID=None, lid=None, rid=None, head=None, flag=None):
        self.ID = ID
        self.lid = lid
        self.rid = rid
        self.head = head
        self.flag = flag

    def __repr__(self):
        return "#{}-{}:{}".format(self.lid, self.rid, self.head)

    def __str__(self):
        return repr(self)


class PredInfo(object):

    def __init__(self, ID=None, pred=None, predtype=None, lemma=None, pos=None, sense=None):
        self.ID = ID
        self.pred = pred
        self.predtype = predtype
        self.lemma = lemma
        self.pos = pos
        self.sense = sense

    @staticmethod
    def from_string(pred_str):
        pred = Predicate.from_string(pred_str)
        return PredInfo(pred=pred_str, predtype=pred.ptype, lemma=pred.lemma, pos=pred.pos, sense=pred.sense)


class RulePred(object):

    def __init__(self, ruleid=None, predid=None, carg=None):
        self.ruleid = ruleid
        self.predid = predid
        self.carg = carg

    def __repr__(self):
        return "RulePred(ruleid={}, predid={}, carg={})".format(self.ruleid, self.predid, self.carg)


# ----------------
# Human annotation
# ----------------

class Word(object):
    """
    Human annotator layer: Words
    """
    def __init__(self, widx=-1, word='', lemma='', pos='', cfrom=-1, cto=-1, sent=None):
        self.ID = None
        if sent:
            self.sid = sent.ID
            self.sent = sent
        else:
            self.sid = -1
            self.sent = None
        self.widx = widx
        self.word = word
        self.pos = pos
        self.lemma = lemma
        self.cfrom = cfrom
        self.cto = cto
        self.comment = ''

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "`{w}`<{cf}:{ct}>".format(w=self.word, cf=self.cfrom, ct=self.cto)


class Concept(object):
    """
    Human annotator layer: Concepts
    """
    def __init__(self, cidx=-1, clemma=None, tag=None, sent=None):
        self.ID = None
        if sent:
            self.sid = sent.ID
            self.sent = sent
        else:
            self.sid = -1
            self.sent = None
        self.cidx = cidx
        self.clemma = clemma
        self.tag = tag
        self.flag = None
        self.comment = ''
        self.words = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "`{lemma}`:{tag}".format(lemma=self.clemma, tag=self.tag)


class CWLink(object):
    """
    Human annotator layer: Word-Concept Links
    """
    def __init__(self, wid=-1, cid=-1):
        self.wid = wid
        self.cid = cid

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "c#{}->w#{}".format(self.cid, self.wid)
