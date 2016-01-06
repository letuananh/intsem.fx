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

from delphin.mrs.components import Pred

from chirptext.leutile import StringTool
from chirptext.leutile import jilog
from chirptext.texttaglib import TagInfo
from chirptext.texttaglib import TaggedSentence
from lelesk import LeLeskWSD # WSDResources
from lelesk.config import LLConfig

from .mwemap import MWE_ERG_PRED_LEMMA

########################################################################



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
    #	cut off is adj in wn but n in ERG???
    #	no dole as a verb in Wordnet
    #	direct should not be a noun
    #	,['church-goer','churchgoer']
    #		#,['line+up','lineup']
    #		#,['the+same','same']
    #	downstairs_n not in WN
    #	# droppings vs dropping?
    #	# east+west => direction?
    #	# intermediary (n in WN) but a???
    #	# no solar_n in WN but there are a lot of [solar x]
    #	# trapdoor => trap door (WN)
    #	#thanks a ? (is n in WN)
    #	# Not in WN:
    #		# attracted_a_to_rel	attracted	a	to	1
    #		# childrens_a_1_rel	childrens	a	1	1
    #		# caribbean (a)
    #	# all modals
    #	# other_n
    #		#re-_a_again_rel	re-	a	again	124
    #		#un-_a_rvrs_rel	un-	a	rvrs	104
    #		#
    #	# else_a_1_rel
    #	# oh_a_1_rel
    #	# colon_v_id_rel
    #	# own_n_1_rel

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
                potential = [x for x in sm[lemma] if x.pos == pos or pos in ('x', 'p')]
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
            preds.append(TagInfo(cfrom, cto, label))
        tagged = TaggedSentence(mrs.sent.text, preds)
        return str(tagged)

def main():
    print("You should NOT see this line. This is a library, not an app")
    pass


if __name__ == "__main__":
    main()
