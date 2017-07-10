#!/usr/bin/env python3
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

import delphin
from delphin.mrs import simplemrs
from delphin.mrs import simpledmrs
from delphin.mrs import dmrx
from delphin.mrs import Mrs
from delphin.mrs import Dmrs
from delphin.mrs.components import Pred
from chirptext.leutile import StringTool
from chirptext.texttaglib import TagInfo
from chirptext.texttaglib import TaggedSentence
from yawlib import Synset
from lelesk import LeLeskWSD
from lelesk import LeskCache  # WSDResources
from .mwemap import MWE_ERG_PRED_LEMMA


########################################################################


logger = logging.getLogger()


class Sentence(object):

    def __init__(self, text='', sid=-1, goldtags=None):
        self.text = StringTool.strip(text)
        self.sid = sid
        self.parses = list()
        self.goldtags = goldtags

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
        if doc_node is not None:
            doc_node.append(sent_node)
        etree.SubElement(sent_node, 'text', text=self.text)
        dmrses_node = etree.SubElement(sent_node, 'dmrses')
        if len(self) > 0:
            for parse in self:
                # tag using custom goldtags if given else self.goldtags
                dmrses_node.append(parse.dmrs().xml())
        return sent_node

    def tag(self, goldtags=None, cgold=None, method=None):
        for parse in self:
            parse.dmrs().tag_xml(goldtags, cgold, method=method, update_back=True)

    def to_xml_str(self, doc_node=None, goldtags=None, pretty_print=True):
        xml_node = self.to_xml_node(doc_node)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    def to_visko_xml(self, method=TagInfo.MFS, goldtags=None, with_raw=True):
        sent_node = etree.Element('sentence')
        sent_node.set('id', str(self.sid))
        sent_node.set('version', '0.1')
        sent_node.set('lang', 'eng')
        # Add license information
        text_node = etree.SubElement(sent_node, 'text')
        text_node.text = self.text
        for id, parse in enumerate(self):
            intp_node = etree.SubElement(sent_node, 'interpretation')
            intp_node.set('id', str(id + 1))
            intp_node.set('mode', 'active' if id == 0 else 'inactive')
            # store MRS raw
            if parse.mrs():
                mrs_node = etree.SubElement(intp_node, 'mrs')
                mrs_node.text = etree.CDATA(parse.mrs().tostring())
            # store DMRS
            intp_node.append(parse.dmrs().xml())
        return sent_node

    def to_visko_xml_str(self, method=TagInfo.MFS, goldtags=None, with_raw=True, pretty_print=True):
        xml_node = self.to_visko_xml(method, goldtags, with_raw)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")


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
        self.tags = tags
        # Visko integration
        self.ID = None
        self.ident = None

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

    def json(self):
        j = Dmrs.to_dict(self.obj(), properties=True)
        # sense-tagging if possible
        # JSON will be tagged with mfs by default
        tags = self.tags if self.tags else self.tag(method=TagInfo.MFS)
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

    def clear(self):
        self._obj = None
        self._node = None

    def preds(self):
        return [self.ep_to_taginfo(x) for x in self.obj().eps()]

    def tagged(self):
        return TaggedSentence(self.sent.text, self.preds())

    def ep_to_taginfo(self, ep):
        # nodeid = ep[0]
        pred = ep[1]
        # label = ep[2]
        # args = ep[3]
        cfrom = -1
        cto = -1
        if len(ep) > 4:
            lnk = ep[4]
            cfrom = int(lnk.data[0])
            cto = int(lnk.data[1])
        pred_string = delphin.mrs.components.normalize_pred_string(pred.string)
        return TagInfo(cfrom, cto, pred_string, source='ep')

    def tag_xml(self, goldtags=None, cgold=None, with_raw=True, method=TagInfo.MFS, update_back=False):
        ''' Sense tag XML'''
        # Use built-in tags if available
        tags = self.tag(goldtags, cgold, method) if not self.tags else self.tags
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
                    else:
                        realpred = node.find('realpred')
                        if realpred is not None:
                            candidate_node = etree.SubElement(node, 'sense')
                            # candidate_node.set('pos', str(tag.synsetid.pos))
                            candidate_node.set('synsetid', str(tag.synsetid))  # [2015-10-26] FCB: synsetid format should be = 12345678-x]
                            candidate_node.set('lemma', str(tag.lemma))
                            candidate_node.set('score', str(tag.tagcount))
                            candidate_node.set('type', tagtype)
        # update self.xml?
        if update_back:
            self.update(root)
        return root

    def pred_candidates(self):
        ''' Get all sense candidates for an MRS)
        '''
        best_candidate_map = {}
        for pred in self.preds():
            candidates = PredSense.search_pred_string(pred.label, False)
            if candidates:
                best_candidate_map[pred_to_key(pred)] = candidates[0]
        return best_candidate_map

    def find_tags(self):
        ''' Find all available sense tags in XML'''
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
            if len(tags.keys()) > 0:
                self.tags = tags
        return self.tags

    SPECIAL_CHARS = '''?!"$-_&|.,;:'''

    def fix_tokenization(self, ep, sent_text=None):
        cfrom = ep.cfrom
        cto = ep.cto
        surface = sent_text[cfrom:cto] if sent_text is not None else ''
        while len(surface) > 0 and surface[0] in self.SPECIAL_CHARS:
            surface = surface[1:]
            cfrom += 1
        while len(surface) > 0 and surface[-1] in self.SPECIAL_CHARS:
            surface = surface[:-1]
            cto -= 1
        return cfrom, cto, surface

    def match(self, tag, ep):
        sent_text = self.parse.sent.text if self.parse is not None and self.parse.sent is not None else None
        cfrom, cto, surface = self.fix_tokenization(ep, sent_text)
        # logging.debug(cfrom, cto, ep.cfrom, ep.cto, ep.pred.lemma)
        if int(tag[1]) == cfrom or tag[1] == ep.cfrom:
            if int(tag[2]) == cto or tag[2] == ep.cto:
                # logging.debug(tag, ep)
                return True
            elif ep.pred.lemma == tag[4] or surface == tag[4]:
                return True
        return False

    def tag(self, goldtags=None, cgold=None, method=TagInfo.MFS):
        ''' Return a map from nodeid to a list of tuples in this format (Synset, sensetype=str)
        method can be set to None to prevent WSD to be performed
        '''
        best_candidate_map = self.pred_candidates()
        if goldtags is None and self.parse is not None and self.parse.sent is not None:
            # try to use parse's sentence's goldtags
            goldtags = self.parse.sent.goldtags
        tags = dd(list)
        eps = self.obj().eps()
        wsd = LeLeskWSD(dbcache=LeskCache())
        context = [p.pred.lemma for p in eps]
        for ep in eps:
            if goldtags:
                for tag in goldtags:
                    # exact matching <cfrom:cto> or cfrom:lemma
                    if self.match(tag, ep):
                        # sense gold
                        # synset | lemma | type
                        sid = tag[3]
                        lemma = tag[4]
                        sense = Synset(sid, lemma=lemma)
                        tags[ep.nodeid].append((sense, TagInfo.GOLD))
                        if cgold:
                            cgold.count('inserted')
            if ep.pred.type in (Pred.REALPRED, Pred.STRINGPRED):
                if method == TagInfo.LELESK:
                    logger.debug("Performing WSD using {} on {}/{}".format(method, ep.pred.lemma, context))
                    scores = wsd.lelesk_wsd(ep.pred.lemma, '', lemmatizing=False, context=context)
                    if scores:
                        # insert the top one
                        candidate = None
                        best = scores[0].candidate.synset
                        # bl = best.terms[0].term if best.terms else ''
                        tags[ep.nodeid].append((Synset(best.sid, lemma=ep.pred.lemma), 'lelesk'))
                elif method == TagInfo.MFS:  # mfs
                    key = '-'.join((str(ep.cfrom), str(ep.cto), str(ep.pred.pos), str(ep.pred.lemma), str(ep.pred.sense)))
                    if key in best_candidate_map:
                        candidate = best_candidate_map[key]
                        tags[ep.nodeid].append((candidate, TagInfo.MFS))
                else:
                    # What should be done here? no tagging at all?
                    pass
        self.tags = tags
        return tags


def pred_to_key(pred):
    pred_obj = Pred.grammarpred(pred.label)
    return '-'.join((str(pred.cfrom), str(pred.cto), str(pred_obj.pos), str(pred_obj.lemma), str(pred_obj.sense)))


class PredSense(object):

    lwsd = LeLeskWSD(dbcache=LeskCache())

    @staticmethod
    def unpack_pred(pred_text):
        parts = pred_text.split('\t')
        if len(parts) == 4:
            return PredStruct._make([StringTool.strip(x) for x in parts])
        else:
            return None

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
        ('st','n'): (('saint',), 'n'),
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
        ('used+to','v'): (('used to',),'a'),
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
                lemmata,pos = (('modal',), 'a')
            elif pred.pos == 'a':
                lemmata,pos = ([pred.lemma], 'n')
            elif pred.pos == 'n':
                lemmata,pos = ([pred.lemma], 'a')
            #-----------
            if isinstance(tracer,list):
                tracer.append((lemmata, pos))
            ss = PredSense.search_sense(lemmata, pos)

        # Done
        return sorted(ss, key=lambda x: x.tagcount, reverse=True)

    @staticmethod
    def sinfo_str(senseinfo):
        return "%s (%s)" % (senseinfo.synsetid, senseinfo.sk)

    @staticmethod
    def tag_sentence(dmrs):
        preds = []
        for taginfo in dmrs.preds():
            cfrom = taginfo.cfrom
            cto = taginfo.cto
            label = taginfo.label
            ss = PredSense.search_pred_string(label, True)
            if ss:
                label += ' | '.join([PredSense.sinfo_str(x) for x in ss])
            preds.append(TagInfo(cfrom, cto, label, source=TagInfo.ISF))
        tagged = TaggedSentence(dmrs.parse.sent.text, preds)
        return str(tagged)

##############################################################################
# MAIN
##############################################################################


def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
