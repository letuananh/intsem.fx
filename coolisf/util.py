#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Utility functions

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
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os

from delphin.interfaces import ace
from delphin.mrs.components import Pred

from chirptext.leutile import StringTool
from chirptext.texttaglib import TagInfo
from chirptext.texttaglib import TaggedSentence
from lelesk import LeLeskWSD # WSDResources
from lelesk.config import LLConfig

from .mwemap import MWE_ERG_WN_MAPPING
from .mwemap import MWE_ERG_PRED_LEMMA

from .model import Sentence

##########################################
# CONFIGURATION
##########################################
ERG_GRAM_FILE = './data/erg.dat'
ACE_BIN = os.path.expanduser('~/bin/ace')
ACE_ARGS = [ '-n', '5' ]
SEMCOR_TXT = 'data/semcor.txt'
TOP_K = 10

########################################################################

def get_preds(dmrs):
    if dmrs:
        return [Pred.normalize_pred_string(x.pred.string) for x in dmrs.nodes]


class Grammar:
    def __init__(self, gram_file=ERG_GRAM_FILE, cmdargs=ACE_ARGS, ace_bin=ACE_BIN):
        self.gram_file = gram_file
        self.cmdargs = cmdargs
        self.ace_bin = ace_bin

    def txt2preds(self, text):
        dmrses = self.txt2dmrs(text)
        if dmrses:
            return [get_preds(x) for x in dmrses]
        else:
            print("Can't parse the sentence [%s]" % (text,))

    def txt2dmrs(self, text):
        s = Sentence(text)

        with ace.AceParser(self.gram_file, executable=self.ace_bin, cmdargs=self.cmdargs) as parser:
            result = parser.interact(text)
            if result and result['RESULTS']:
                top_res = result['RESULTS']
                for mrs in top_res:
                    s.add(mrs['MRS'])
        return s


class PredSense():
    
    lwsd = LeLeskWSD(LLConfig.WORDNET_30_GLOSS_DB_PATH, LLConfig.WORDNET_30_PATH)
    
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
        return potential

    singleton_sm = None

    @staticmethod
    def search_sense(lemmata, pos):
        if PredSense.singleton_sm is None:
            PredSense.singleton_sm = PredSense.lwsd.wn.all_senses()
        sm = PredSense.singleton_sm

        for lemma in lemmata:
            if lemma in sm:
                potential = [x for x in sm[lemma] if x.pos == pos]
                if potential:
                    return potential
        return []

    # alias
    def search_pred_string(pred_str,extend_lemma=True): 
        if pred_str in MWE_ERG_PRED_LEMMA:
            pred = Pred.grammarpred(pred_str)
            ss = PredSense.search_sense([MWE_ERG_PRED_LEMMA[pred_str]], pred.pos)
            #print("Looking at %s" % (pred_str))
            #if ss:
            #    print("MWE detected")
            return sorted(ss, key=lambda x: x.tagcount, reverse=True)
        else:
            return PredSense.search_pred(Pred.grammarpred(pred_str), extend_lemma)

    @staticmethod
    def search_pred(pred, auto_expand=True):
        # if pred in MWE_ERG_WN_MAPPING:
        if not pred:
            return None
        
        if auto_expand:
            ss = PredSense.search_sense(PredSense.extend_lemma(pred.lemma), pred.pos)
        else:
            ss = PredSense.search_sense([pred.lemma], pred.pos)

        # hardcode: try to match noun & adj/v
        if not ss and auto_expand:
            # hard code modal
            if pred.lemma in PredSense.MODAL_VERBS and pred.pos == 'v':
                ss = PredSense.search_sense(('modal',), 'a')
            elif pred.lemma == 'st' and pred.pos == 'n':
                ss = PredSense.search_sense(('saint',), 'n')
            elif pred.lemma == 'children':
                ss = PredSense.search_sense(('child',), pred.pos)
            elif pred.lemma == 'trapdoor':
                ss = PredSense.search_sense(('trap door',), pred.pos)
            elif pred.lemma == 'declining':
                ss = PredSense.search_sense(('decline',), pred.pos)
            elif pred.lemma == 'allright':
                ss = PredSense.search_sense(('alright',), pred.pos)
            elif pred.lemma == 'a+couple':
                ss = PredSense.search_sense(('a couple of',), pred.pos)
            elif pred.lemma == 'diagnostic':
                ss = PredSense.search_sense(('diagnostics',), pred.pos)
            elif pred.lemma == 'suburbian':
                ss = PredSense.search_sense(('suburban',), pred.pos)
            elif pred.lemma == 'or+not':
                ss = PredSense.search_sense(('not',), pred.pos)
            elif pred.lemma == 'undoubted':
                ss = PredSense.search_sense(('undoubtedly',), pred.pos)
            elif pred.lemma == 'used+to' and pred.pos == 'v':
                ss = PredSense.search_sense(('used to',), 'a')
            elif pred.lemma == 'had+better':
                ss = PredSense.search_sense(('better',), pred.pos)
            elif pred.lemma == 'little-few':
                ss = PredSense.search_sense(('few',), pred.pos)
            elif pred.lemma == 'much-many':  # should we check the surface form and then match it? REF: little-few
                ss = PredSense.search_sense(('many',), pred.pos)
            #            elif pred.lemma == 'the+same':
            #               ss=PredSense.search_sense(('same',), pred.pos)
            elif pred.pos == 'a':
                ss = PredSense.search_sense([pred.lemma], 'n')
            elif pred.pos == 'n':
                ss = PredSense.search_sense([pred.lemma], 'a')
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
            preds.append(TagInfo(cfrom, cto, label))
        tagged = TaggedSentence(mrs.sent.text, preds)
        return str(tagged)

def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
