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
from yawlib.models import SenseInfo
from lelesk import LeLeskWSD  # WSDResources
from .mwemap import MWE_ERG_PRED_LEMMA


########################################################################


class Sentence(object):

    def __init__(self, text='', sid=-1, goldtags=None):
        self.text = StringTool.strip(text)
        self.sid = sid
        self.mrses = list()
        self.goldtags = goldtags

    def add(self, mrs):
        self.mrses.append(DMRS(StringTool.strip(mrs), sent=self))

    def __len__(self):
        return len(self.mrses)

    def add_from_xml(self, xml):
        self.mrses.append(DMRS(dmrs_xml=xml, sent=self))

    def __str__(self):
        return "%s (%s mrs(es))" % (self.text, len(self.mrses))

    def to_xml_node(self, doc_node=None, goldtags=None):
        sent_node = etree.Element('sentence', sid=str(self.sid))
        if doc_node is not None:
            doc_node.append(sent_node)
        etree.SubElement(sent_node, 'text', text=self.text)
        dmrses_node = etree.SubElement(sent_node, 'dmrses')
        if len(self.mrses) > 0:
            for mrs in self.mrses:
                # tag using custom goldtags if given else self.goldtags
                dmrs_node = mrs.sense_tag(goldtags if goldtags else self.goldtags)
                dmrses_node.append(dmrs_node)
        return sent_node

    def to_xml_str(self, doc_node=None, goldtags=None, pretty_print=True):
        xml_node = self.to_xml_node(doc_node, goldtags)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")

    def to_visko_xml(self, method='mfs', goldtags=None, with_raw=True):
        sent_node = etree.Element('sentence')
        sent_node.set('id', str(self.sid))
        sent_node.set('version', '0.1')
        sent_node.set('lang', 'eng')
        # Add license information
        text_node = etree.SubElement(sent_node, 'text')
        text_node.text = self.text
        for id, mrs in enumerate(self.mrses):
            intp_node = etree.SubElement(sent_node, 'interpretation')
            intp_node.set('id', str(id))
            intp_node.set('mode', 'active' if id == 0 else 'inactive')
            # store MRS raw
            if mrs.text:
                mrs_node = etree.SubElement(intp_node, 'mrs')
                mrs_node.text = mrs.text
            # store DMRS
            # tag using given goldtags else self.goldtags
            dmrs_node = mrs.sense_tag(goldtags=goldtags if goldtags else self.goldtags, with_raw=with_raw, method='mfs')
            intp_node.append(dmrs_node)
        return sent_node

    def to_visko_xml_str(self, method='mfs', goldtags=None, with_raw=True, pretty_print=True):
        xml_node = self.to_visko_xml(method, goldtags, with_raw)
        return etree.tostring(xml_node, pretty_print=pretty_print, encoding="utf-8").decode("utf-8")


class DMRS(object):
    def __init__(self, mrs_text=None, dmrs_xml=None, sent=None):
        self.sent = sent
        self.text = mrs_text
        self.dmrs_xml_raw = dmrs_xml
        self.mrs_obj = None
        self.dmrs_node = None

    def mrs(self):
        if self.mrs_obj is None:
            if self.text:
                self.mrs_obj = simplemrs.loads_one(self.text)
            elif self.dmrs_xml_raw:
                mrses = list(dmrx.deserialize(io.StringIO(self.dmrs_xml_raw)))
                if len(mrses) == 1:
                    self.mrs_obj = mrses[0]
            else:
                raise Exception("Invalid DMRS XML")
        return self.mrs_obj

    def dmrs_xml_str(self, pretty_print=False):
        return dmrx.dumps([self.mrs()], pretty_print=pretty_print)

    def dmrs_xml(self, pretty_print=False, with_raw=False):
        ''' Export DMRS as an XML node
        '''
        self.dmrs_node = etree.XML(self.dmrs_xml_str(pretty_print))[0]
        if with_raw:
            raw_node = etree.Element('raw')
            raw_node.text = etree.CDATA(self.mrs_str())
            self.dmrs_node.insert(0, raw_node)
        return self.dmrs_node

    def mrs_json(self):
        return Mrs.to_dict(self.mrs(), properties=True)
    
    def mrs_json_str(self):
        '''MRS data in JSON format'''
        return json.dumps(self.mrs_json())

    def mrs_str(self, pretty_print=True):
        '''prettified MRS string'''
        return simplemrs.dumps_one(self.mrs(), pretty_print=pretty_print)

    def dmrs_json(self):
        j = Dmrs.to_dict(self.mrs(), properties=True)
        # Add pred type and pos
        for node, ep in zip(j['nodes'], self.mrs().eps()):
            node['type'] = 'gpred' if (ep.pred.type == Pred.GRAMMARPRED) else 'realpred'
            if ep.pred.pos:
                node['pos'] = ep.pred.pos
        # Remove empty rargname
        for link in j['links']:
            if link['rargname'] is None:
                link['rargname'] == ''
        return j

    def dmrs_json_str(self):
        '''DMRS data in JSON format'''
        return json.dumps(self.dmrs_json())

    def dmrs_str(self):
        '''prettified DMRS string'''
        return simpledmrs.dumps_one(self.mrs(), pretty_print=True)

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.mrs_str()

    def surface(self, node):
        if not node or not self.sent:
            return None
        else:
            return self.sent.text[int(node.cfrom):int(node.cto)]

    def clear(self):
        self.mrs_obj = None
        self.dmrs_node = None

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

    def preds(self):
        return [self.ep_to_taginfo(x) for x in self.mrs().eps()]

    def sense_tag(self, goldtags=None, cgold=None, with_raw=True, method='mfs'):
        '''
        Return a sense-tagged XML node
        '''
        tags = self.tag(goldtags, cgold, method)
        dmrs = self.dmrs_xml(with_raw=with_raw)
        for node in dmrs.findall('node'):
            if int(node.get('nodeid')) in tags:
                ntags = tags[int(node.get('nodeid'))]
                for tag, tagtype in ntags:
                    if tagtype == TagInfo.GOLD:
                        gold_node = etree.SubElement(node, 'sensegold')
                        gold_node.set('synset', str(tag.synsetid))
                        gold_node.set('clemma', tag.lemma)
                    else:
                        realpred = node.find('realpred')
                        if realpred is not None:
                            candidate_node = etree.SubElement(node, 'sense')
                            # candidate_node.set('pos', str(tag.synsetid.pos))
                            candidate_node.set('synsetid', str(tag.synsetid))  # [2015-10-26] FCB: synsetid format should be = 12345678-x]
                            candidate_node.set('lemma', str(tag.lemma))
                            candidate_node.set('score', str(tag.tagcount))
        return dmrs

    def sense_tag_json(self, goldtags=None, cgold=None, method='mfs'):
        tags = self.tag(goldtags, cgold, method)
        j = self.dmrs_json()
        for node in j['nodes']:
            nid = node['nodeid']
            if nid in tags and len(tags[nid]) > 0:
                node['senses'] = []
                for tag, tagtype in tags[nid]:
                    node['senses'].append({'synsetid': str(tag.synsetid), 'lemma': tag.lemma, 'type': tagtype})
        return j

    def sense_tag_json_str(self, goldtags=None, cgold=None, method='mfs'):
        return json.dumps(self.sense_tag_json(goldtags, cgold, method))

    def pred_candidates(self):
        ''' Get all sense candidates for a particular MRS)
        '''
        best_candidate_map = {}
        for pred in self.preds():
            candidates = PredSense.search_pred_string(pred.label, False)
            if candidates:
                best_candidate_map[pred_to_key(pred)] = candidates[0]
        return best_candidate_map

    def tag(self, goldtags=None, cgold=None, method='mfs'):
        best_candidate_map = self.pred_candidates()
        tags = dd(list)
        eps = self.mrs().eps()
        wsd = LeLeskWSD()
        context = [p.pred.lemma for p in eps]
        for ep in eps:
            if goldtags:
                for tag in goldtags:
                    if int(tag[1]) == ep.cfrom and int(tag[2]) == ep.cto:
                        # sense gold
                        # synset | lemma | type
                        sid = tag[3]
                        lemma = tag[4]
                        sense = SenseInfo(sid, lemma=lemma)
                        tags[ep.nodeid].append((sense, 'gold'))
                        if cgold:
                            cgold.count('inserted')
            if ep.pred.type in (Pred.REALPRED, Pred.STRINGPRED):
                if method == 'lelesk':
                    scores = wsd.lelesk_wsd(ep.pred.lemma, '', lemmatizing=False, context=context)
                    if scores:
                        # insert the top one
                        candidate = None
                        best = scores[0].candidate.synset
                        # bl = best.terms[0].term if best.terms else ''
                        tags[ep.nodeid].append((SenseInfo(best.sid, lemma=ep.pred.lemma), 'lelesk'))
                else:  # mfs
                    key = '-'.join((str(ep.cfrom), str(ep.cto), str(ep.pred.pos), str(ep.pred.lemma), str(ep.pred.sense)))
                    if key in best_candidate_map:
                        candidate = best_candidate_map[key]
                        tags[ep.nodeid].append((candidate, 'mfs'))
        return tags


def tag_dmrs_xml(mrs, dmrs, goldtags=None, cgold=None):
    best_candidate_map = mrs.pred_candidates()
    for node in dmrs.findall('node'):
        if goldtags:
            for tag in goldtags:
                if node.get('cfrom') and node.get('cto') and int(tag[1]) == int(node.get('cfrom')) and int(tag[2]) == int(node.get('cto')):
                    gold_node = etree.SubElement(node, 'sensegold')
                    gold_node.set('synset', tag[3])
                    gold_node.set('clemma', tag[4])
                    if cgold:
                        cgold.count('inserted')
        realpred = node.find('realpred')
        if realpred is not None:
            # insert mcs
            key = '-'.join((str(node.get('cfrom')), str(node.get('cto')), str(realpred.get('pos')), str(realpred.get('lemma')), str(realpred.get('sense'))))
            if key in best_candidate_map:
                candidate = best_candidate_map[key]
                candidate_node = etree.SubElement(node, 'sense')
                candidate_node.set('pos', str(candidate.synsetid.pos))
                candidate_node.set('synsetid', str(candidate.synsetid))  # [2015-10-26] FCB: synsetid format should be = 12345678-x]
                candidate_node.set('lemma', str(candidate.lemma))
                candidate_node.set('score', str(candidate.tagcount))


def pred_to_key(pred):
    pred_obj = Pred.grammarpred(pred.label)
    return '-'.join((str(pred.cfrom), str(pred.cto), str(pred_obj.pos), str(pred_obj.lemma), str(pred_obj.sense)))


class PredSense(object):

    lwsd = LeLeskWSD()

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
    def search_pred_string(pred_str,extend_lemma=True, tracer=None):
        if pred_str is None:
            return []
        
        if pred_str.startswith("_"):
            pred_str = pred_str[1:]
        
        if pred_str in MWE_ERG_PRED_LEMMA:
            pred = Pred.grammarpred(pred_str)
            if isinstance(tracer,list):
                tracer.append(([MWE_ERG_PRED_LEMMA[pred_str]], pred.pos, 'MWE', 'See also?: ' + Pred.grammarpred(pred_str).lemma))
            ss = PredSense.search_sense([MWE_ERG_PRED_LEMMA[pred_str]], pred.pos)
            #print("Looking at %s" % (pred_str))
            #if ss:
            #    print("MWE detected")
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
        pos     = pred.pos

        if (lemmata, pos) in PredSense.AUTO_EXTEND:
            lemmata, pos = PredSense.AUTO_EXTEND[(lemmata, pos)]
        elif (lemmata,) in PredSense.AUTO_EXTEND:
            lemmata = PredSense.AUTO_EXTEND[(lemmata,)]

        if isinstance(tracer,list):
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
        return "%s-%s (%s)" % (senseinfo.sid, senseinfo.pos, senseinfo.sk)

    @staticmethod
    def tag_sentence(mrs):
        preds = []
        for taginfo in mrs.preds():
            cfrom = taginfo.cfrom
            cto = taginfo.cto
            label = taginfo.label
            # pred = Pred.grammarpred(label)
            # ss = PredSense.search_pred(pred, True)
            ss = PredSense.search_pred_string(label, True)
            if ss:
                label += ' | '.join([PredSense.sinfo_str(x) for x in ss])
            preds.append(TagInfo(cfrom, cto, label, source=TagInfo.ISF))
        tagged = TaggedSentence(mrs.sent.text, preds)
        return str(tagged)

##############################################################################
# MAIN
##############################################################################


def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
