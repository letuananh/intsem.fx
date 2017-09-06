# -*- coding: utf-8 -*-

'''
Basic data models

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
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################


import io
import json
import logging
from collections import defaultdict as dd

from lxml import etree


from delphin.extra.latex import dmrs_tikz_dependency
from delphin.mrs import simplemrs
from delphin.mrs import simpledmrs
from delphin.mrs import dmrx
from delphin.mrs import Mrs
from delphin.mrs import Dmrs
from delphin.mrs.components import Pred
from delphin.mrs.components import normalize_pred_string
from chirptext.leutile import StringTool
from chirptext.texttaglib import TagInfo
from yawlib import Synset
from lelesk import LeLeskWSD
from lelesk import LeskCache  # WSDResources
from .mwemap import MWE_ERG_PRED_LEMMA


########################################################################


logger = logging.getLogger()


class Sentence(object):

    def __init__(self, text='', sid=-1):
        self.text = StringTool.strip(text)
        self.sid = sid
        self.shallow = None
        self.comment = None
        self.flag = None
        self.parses = list()

    def add(self, mrs_str=None, dmrs_xml=None):
        p = Parse(mrs_str, dmrs_xml, self)
        self.parses.append(p)
        return p

    def __getitem__(self, key):
        return self.parses[key]

    def __len__(self):
        return len(self.parses)

    def __str__(self):
        return "%s (%s mrs(es))" % (self.text, len(self))

    def to_xml_node(self, doc_node=None):
        sent_node = etree.Element('sentence', sid=str(self.sid))
        # store flag
        if self.flag is not None:
            sent_node.set('flag', str(self.flag))
        if doc_node is not None:
            doc_node.append(sent_node)
        text_node = etree.SubElement(sent_node, 'text')
        text_node.text = self.text
        # store comment
        if self.comment is not None:
            comment_node = etree.SubElement(sent_node, 'comment')
            comment_node.text = etree.CDATA(self.comment)
        dmrses_node = etree.SubElement(sent_node, 'dmrses')
        if len(self) > 0:
            for parse in self:
                dmrses_node.append(parse.dmrs().xml())
        return sent_node

    def tag(self, method=None):
        for parse in self:
            parse.dmrs().tag(method=method)
        return self

    def tag_xml(self, method=None, update_back=True):
        for parse in self:
            parse.dmrs().tag_xml(method=method, update_back=update_back)
        return self

    def to_xml_str(self, doc_node=None, pretty_print=True):
        xml_node = self.to_xml_node(doc_node)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    def to_visko_xml(self, with_raw=True):
        sent_node = etree.Element('sentence')
        sent_node.set('id', str(self.sid))
        sent_node.set('version', '0.1')
        sent_node.set('lang', 'eng')
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
        for id, parse in enumerate(self):
            intp_node = etree.SubElement(sent_node, 'reading')
            intp_node.set('id', str(id + 1))
            intp_node.set('mode', 'active' if id == 0 else 'inactive')
            # store MRS raw
            if parse.mrs():
                mrs_node = etree.SubElement(intp_node, 'mrs')
                mrs_node.text = etree.CDATA(parse.mrs().tostring())
            # store DMRS
            intp_node.append(parse.dmrs().xml())
            # store shallow if needed
            if self.shallow:
                shallow_node = etree.SubElement(sent_node, 'shallow')
                shallow_node.text = json.dumps(self.shallow.to_json())
        return sent_node

    def to_visko_xml_str(self, with_raw=True, pretty_print=True):
        xml_node = self.to_visko_xml(with_raw)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    def to_latex(self):
        return dmrs_tikz_dependency([p.dmrs().obj() for p in self])


class Parse(object):

    def __init__(self, mrs_raw=None, dmrs_raw=None, sent=None):
        self._mrs = None  # These should never be accessed directly
        self._dmrs = None
        if mrs_raw is not None and len(mrs_raw) > 0:
            self.mrs(mrs_raw)
        if dmrs_raw is not None and len(dmrs_raw) > 0:
            self.dmrs(dmrs_raw)
        self.sent = sent
        self.ID = None  # Visko integration
        self.ident = None  # Visko integration

    def update_mrs(self):
        if self._dmrs is not None:
            self._mrs = self.dmrs().to_mrs()

    def update_dmrs(self, with_raw=True):
        if self._mrs:
            self._dmrs = self.mrs().to_dmrs(with_raw=True)

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


class MRS(object):

    def __init__(self, mrs_raw, parse=None):
        self._raw = mrs_raw
        self._obj = None
        self.parse = parse

    def __str__(self):
        return self.tostring()

    def obj(self):
        ''' Get pydelphin MRS object
        '''
        if self._obj is None:
            self._obj = simplemrs.loads_one(self._raw)
        return self._obj

    def json(self):
        return Mrs.to_dict(self.obj(), properties=True)

    def json_str(self):
        '''MRS data in JSON format'''
        return json.dumps(self.json())

    def tostring(self, pretty_print=True):
        '''prettified MRS string'''
        return simplemrs.dumps_one(self.obj(), pretty_print=pretty_print)

    def to_dmrs(self, with_raw=True):
        xml_str = dmrx.serialize([self.obj()])
        dmrs_node = etree.XML(xml_str)[0]
        # insert RAW to dmrs_xml
        if with_raw:
            raw_node = etree.Element('raw')
            raw_node.text = etree.CDATA(self.tostring())
            dmrs_node.insert(0, raw_node)
        return DMRS(etree.tostring(dmrs_node).decode('utf-8'), parse=self.parse)


class DMRS(object):
    def __init__(self, dmrs_xml=None, parse=None, tags=None):
        self.parse = parse
        # Internal properties, should NOT be accessed directly
        self._raw = dmrs_xml  # only support DMRS XML format for now
        self._obj = None  # pydelphin object
        self._node = None  # xml_node
        self.tags = tags if tags else dd(list)
        # Visko integration
        self.ID = None
        self.ident = None
        # find tags in XML if available
        self.find_tags()

    def update(self, xml_node):
        self._node = xml_node
        self._raw = etree.tostring(xml_node).decode('utf-8')

    def obj(self):
        ''' Get pydelphin DMRS object
        '''
        if self._obj is None:
            mrses = list(dmrx.deserialize(io.StringIO(self._raw)))
            if len(mrses) == 1:
                self._obj = mrses[0]
                # store available tags
                self.find_tags()
            else:
                raise Exception("Invalid DMRS XML")
        return self._obj

    def to_mrs(self):
        mrs_str = simplemrs.dumps_one(self.obj())
        return MRS(mrs_str, self.parse)

    #----------------------------
    # Support different formats
    #----------------------------

    def xml(self):
        if self._node is None:
            # reparse DMRS node
            # should tag be re-inserted here?
            self._node = etree.XML(self._raw)
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
        # [2017-07-26] Don't tag JSON by default
        tags = self.tags if self.tags else self.tag(method=TagInfo.DEFAULT)
        for node in j['nodes']:
            nid = node['nodeid']
            if nid in tags and len(tags[nid]) > 0:
                node['senses'] = []
                # sort by WSD method
                tags[nid].sort(key=lambda x: 1 if x[1] == TagInfo.GOLD else 10 if x[1] == TagInfo.LELESK else 50 if TagInfo.MFS else 100)
                for tag, tagtype in tags[nid]:
                    node['senses'].append({'synsetid': str(tag.synsetid), 'lemma': tag.lemma, 'type': tagtype})
        # These are for visko
        # add sentence text if it's available
        if self.parse is not None and self.parse.sent is not None:
            j['text'] = self.parse.sent.text
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
        '''DMRS data in JSON format'''
        try:
            return json.dumps(self.json())
        except:
            return None

    def tostring(self, pretty_print=True):
        '''prettified DMRS string'''
        return simpledmrs.dumps_one(self.obj(), pretty_print=pretty_print)

    def __str__(self):
        return self.tostring()

    def surface(self, node):
        if node is None or self.parse is None or self.parse.sent is None:
            return None
        else:
            return self.parse.sent.text[int(node.cfrom):int(node.cto)]

    def preds(self):
        ''' Get all pred strings '''
        return [normalize_pred_string(x.pred.string) for x in self.obj().eps()]

    def clear(self):
        self._obj = None
        self._node = None

    #-------------------------------
    # Read & write tags from/to XML
    #-------------------------------

    def find_tags(self):
        ''' Find all available sense tags that are stored in XML'''
        root = self.xml()
        if root is not None:
            tags = dd(list)
            nodes = root.findall('./node')
            for n in nodes:
                # find all sense nodes
                sense_nodes = n.findall('sense')
                if sense_nodes is None:
                    sense_nodes = []
                sg = n.find('sensegold')
                if sg is not None:
                    sense_nodes.append(sg)
                    sg.attrib['method'] = TagInfo.GOLD
                for s in sense_nodes:
                    nodeid = int(n.attrib['nodeid'])
                    sid = s.attrib['synsetid']
                    lemma = s.attrib['lemma']
                    score = s.attrib['score'] if 'score' in s.attrib else None
                    method = s.attrib['method'] if 'method' in s.attrib else TagInfo.ISF
                    sinfo = Synset(sid, lemma=lemma)
                    if score is not None:
                        sinfo.tagcount = score
                    tags[nodeid].append((sinfo, method))
            # end for
            # tag list is stored esp for JSON
            if tags:
                self.tags.update(tags)
        return self.tags

    def tag_xml(self, with_raw=True, method=TagInfo.MFS, update_back=False):
        ''' Generate an XML object with available tags
        (perform provided sense-tagging method if required) '''
        # Sense-tagging only if required
        tags = self.tag(method) if not self.tags else self.tags
        root = self.xml()
        for node in root.findall('node'):
            if int(node.get('nodeid')) in tags:
                ntags = tags[int(node.get('nodeid'))]
                for tag, tagtype in ntags:
                    if tagtype == TagInfo.GOLD:
                        gold_node = etree.SubElement(node, 'sensegold')
                        gold_node.set('synsetid', str(tag.synsetid))
                        gold_node.set('lemma', tag.lemma)
                        gold_node.set('type', tagtype)
                    elif tagtype in (TagInfo.MFS, TagInfo.LELESK):
                        realpred = node.find('realpred')
                        if realpred is not None:
                            candidate_node = etree.SubElement(node, 'sense')
                            # candidate_node.set('pos', str(tag.synsetid.pos))
                            candidate_node.set('synsetid', str(tag.synsetid))  # [2015-10-26] FCB: synsetid format should be = 12345678-x]
                            candidate_node.set('lemma', str(tag.lemma))
                            candidate_node.set('score', str(tag.tagcount))
                            candidate_node.set('type', tagtype)
                    else:
                        # DEFAULT? etc.
                        # Do nothing for now
                        pass
        # update self.xml?
        if update_back:
            self.update(root)
        return root

    #-------------------------------
    # Sense-tagging
    #-------------------------------

    def tag(self, method=TagInfo.MFS):
        ''' Sense tag this DMRS using a WSD method (by default is most-frequent sense)
        and then return a map from nodeid to a list of tuples in this format (Synset, sensetype=str)
        '''
        if method is None or method == TagInfo.DEFAULT:
            return {}  # no tag
        tags = self.tags if self.tags else dd(list)
        eps = self.obj().eps()
        wsd = LeLeskWSD(dbcache=LeskCache())
        context = [p.pred.lemma for p in eps]
        for ep in eps:
            if ep.pred.type in (Pred.REALPRED, Pred.STRINGPRED):
                # taggable eps
                if method == TagInfo.LELESK:
                    # TODO: Use POS for better sense-tagging?
                    logger.debug("Performing WSD using {} on {}/{}".format(method, ep.pred.lemma, context))
                    scores = wsd.lelesk_wsd(ep.pred.lemma, '', lemmatizing=False, context=context)
                    if scores:
                        # insert the top one
                        best = scores[0].candidate.synset
                        tags[ep.nodeid].append((Synset(best.sid, lemma=ep.pred.lemma), 'lelesk'))
                elif method == TagInfo.MFS:
                    candidates = PredSense.search_pred_string(ep.pred.string, False)
                    if candidates:
                        tags[ep.nodeid].append((candidates[0], TagInfo.MFS))
                else:
                    # What should be done here? no tagging at all?
                    pass
        self.tags = tags
        return tags


class PredSense(object):

    lwsd = LeLeskWSD(dbcache=LeskCache())

    MODAL_VERBS = ('would', 'could', 'may', 'must', 'should', 'might', 'going+to', 'ought')

    REPLACE_TEMPLATES = [
        ['-', ' ']
        , ['-', '']
        , ['-', '+']
        , ['_', ' ']
        , ['_', '']
        , ['+', ' ']
        , ['+', '-']
        , ['+', '']
        , [' ', '-']
        , [' ', '']
    ]
    #   cut off is adj in wn but n in ERG???
    #   no dole as a verb in Wordnet
    #   direct should not be a noun
    #   ,['church-goer','churchgoer']
    #       #,['line+up','lineup']
    #       #,['the+same','same']
    #   downstairs_n not in WN
    #   # droppings vs dropping?
    #   # east+west => direction?
    #   # intermediary (n in WN) but a???
    #   # no solar_n in WN but there are a lot of [solar x]
    #   # trapdoor => trap door (WN)
    #   #thanks a ? (is n in WN)
    #   # Not in WN:
    #       # attracted_a_to_rel    attracted   a   to  1
    #       # childrens_a_1_rel childrens   a   1   1
    #       # caribbean (a)
    #   # all modals
    #   # other_n
    #       #re-_a_again_rel    re- a   again   124
    #       #un-_a_rvrs_rel un- a   rvrs    104
    #       #
    #   # else_a_1_rel
    #   # oh_a_1_rel
    #   # colon_v_id_rel
    #   # own_n_1_rel

    @staticmethod
    def extend_lemma(lemma):
        potential = set()
        potential.add(lemma)
        for rfrom, rto in PredSense.REPLACE_TEMPLATES:
            if rfrom in lemma:
                potential.add(lemma.replace(rfrom, rto))
        # add lower case
        potential.add(lemma.lower())
        # add +/-
        potential.add(lemma + '+')
        potential.add(lemma + '-')
        # negations & determiners
        if lemma.startswith('not+') or lemma.startswith('the+'):
            potential.add(lemma[4:])
        # add WNL
        potential.add(PredSense.lwsd.lemmatize(lemma))
        return tuple(potential)

    singleton_sm = None

    @staticmethod
    def search_sense(lemmata, pos):
        if PredSense.singleton_sm is None:
            PredSense.singleton_sm = PredSense.lwsd.wn.all_senses()
        sm = PredSense.singleton_sm

        for lemma in lemmata:
            if lemma in sm:
                potential = [x for x in sm[lemma] if x.synsetid.pos == pos or pos in ('x', 'p')]
                if potential:
                    return potential
        return []

    # alias
    def search_pred_string(pred_str, extend_lemma=True, tracer=None):
        if pred_str is None:
            return []
        # if pred_str.startswith("_"):
        #     pred_str = pred_str[1:]
        if pred_str in MWE_ERG_PRED_LEMMA:
            pred = Pred.string_or_grammar_pred(pred_str)
            if isinstance(tracer, list):
                tracer.append(([MWE_ERG_PRED_LEMMA[pred_str]], pred.pos, 'MWE', 'See also?: ' + Pred.grammarpred(pred_str).lemma))
            ss = PredSense.search_sense([MWE_ERG_PRED_LEMMA[pred_str]], pred.pos)
            return sorted(ss, key=lambda x: x.tagcount, reverse=True)
        else:
            return PredSense.search_pred(Pred.grammarpred(pred_str), extend_lemma, tracer)

    AUTO_EXTEND = {
        ('st', 'n'): (('saint',), 'n'),
        ('children',): ('child',),
        ('childrens',): ('child',),
        ('trapdoor',): ('trap door',),
        ('declining',): ('decline',),
        ('allright',): ('alright',),
        ('a+couple',): ('a couple of',),
        ('diagnostic',): ('diagnostics',),
        ('had+better',): ('better',),
        ('suburbian',): ('suburban',),
        ('little-few',): ('few',),
        ('much-many',): ('many',),
        ('or+not',): ('not',),
        ('undoubted',): ('undoubtedly',),
        ('used+to', 'v'): (('used to',), 'a'),
    }

    # [TODO]:
    # significantly: x vs r
    # _along_p_rel
    # if pos ==  x or p => ignore POS
    #
    # slurp        : n vs v (in WN)
    # _add_v_up-to_rel >>> add up
    # _make_v_up-for_rel
    # _come_v_up_rel
    # _duck_v_out_rel
    # _crumble_n_1_rel >>> checked a but v in WN

    @staticmethod
    def search_pred(pred, auto_expand=True, tracer=None):
        if not pred:
            return None

        lemmata = (pred.lemma,) if not auto_expand else PredSense.extend_lemma(pred.lemma)
        pos = pred.pos

        if (lemmata, pos) in PredSense.AUTO_EXTEND:
            lemmata, pos = PredSense.AUTO_EXTEND[(lemmata, pos)]
        elif (lemmata,) in PredSense.AUTO_EXTEND:
            lemmata = PredSense.AUTO_EXTEND[(lemmata,)]

        if isinstance(tracer, list):
            tracer.append((lemmata, pos))
        ss = PredSense.search_sense(lemmata, pos)

        # hardcode: try to match noun & adj/v
        if not ss and auto_expand:
            # hard code modal
            if pred.lemma in PredSense.MODAL_VERBS and pred.pos == 'v':
                lemmata, pos = (('modal',), 'a')
            elif pred.pos == 'a':
                lemmata, pos = ([pred.lemma], 'n')
            elif pred.pos == 'n':
                lemmata, pos = ([pred.lemma], 'a')
            #-----------
            if isinstance(tracer, list):
                tracer.append((lemmata, pos))
            ss = PredSense.search_sense(lemmata, pos)

        # Done
        return sorted(ss, key=lambda x: x.tagcount, reverse=True)


##############################################################################
# MAIN
##############################################################################

if __name__ == "__main__":
    print("You should NOT see this line. This is a library, not an app")
