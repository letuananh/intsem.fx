# -*- coding: utf-8 -*-

'''
ERG-Wordnet mapping

Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

########################################################################

import logging
from delphin.mrs.components import Pred

from yawlib import SynsetCollection
from yawlib.helpers import get_wn
from coolisf.mappings.mwemap import MWE_ERG_PRED_LEMMA


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------

class PredSense(object):

    wn = get_wn()

    MODAL_VERBS = ('would', 'could', 'may', 'must', 'should', 'might', 'going+to', 'ought')
    PREPOSITIONS = ['of', 'to', 'on', 'as']
    IGNORED_GPREDS = ('named', 'a_q',
                      'time_n_rel', 'person_n_rel', 'place_n_rel', 'thing_n_rel', 'manner_n_rel',
                      'reason_n_rel')
    REPLACE_TEMPLATES = [['-', ' '],
                         ['-', ''],
                         ['-', '_'],
                         ['-', '+'],
                         ['_', ' '],
                         ['_', ''],
                         ['+', ' '],
                         ['+', '-'],
                         ['+', ''],
                         [' ', '-'],
                         [' ', '']]
    MANUAL_MAP = {'neg_rel': ('00024073-r',)}

    @staticmethod
    def extend_lemma(lemma):
        ''' Get a set of potential lemmas '''
        potential = set()
        potential.add(lemma)
        for rfrom, rto in PredSense.REPLACE_TEMPLATES:
            potential.add(lemma.replace(rfrom, rto))
        # add lower case
        potential.add(lemma.lower())
        # negations & determiners
        if lemma.startswith('not+') or lemma.startswith('the+'):
            potential.add(lemma[4:])
        getLogger().debug("Potential for `{}': {}".format(lemma, potential))
        # remove prepositions as well
        no_preps = set()
        for p in potential:
            parts = p.split()
            if parts[-1] in PredSense.PREPOSITIONS:
                parts = parts[:-1]
                if parts:
                    no_preps.add(' '.join(parts))
        potential.update(no_preps)
        return potential

    singleton_sm = None

    @staticmethod
    def search_sense(lemmata, pos=None, ctx=None):
        if ctx is None:
            with PredSense.wn.ctx() as ctx:
                return PredSense.search_sense(lemmata, pos=pos, ctx=ctx)
        # ctx is ensured to be not null
        ''' Return a SynsetCollection '''
        if pos and pos in ('x', 'p'):
            pos = None
        potential = SynsetCollection()
        getLogger().debug("search sense lemmas={} (pos={})".format(lemmata, pos))
        for lemma in lemmata:
            synsets = PredSense.wn.search(lemma, pos=pos, ctx=ctx)
            getLogger().debug("search_sense: {} (pos={}): {}".format(lemma, pos, synsets))
            for synset in synsets:
                if synset.ID not in potential:
                    potential.add(synset)
        return potential

    # alias
    def search_pred_string(pred_str, extend_lemma=True, ctx=None):
        if not pred_str:
            raise Exception("pred_str cannot be empty")
        if ctx is None:
            with PredSense.wn.ctx() as ctx:
                return PredSense.search_pred_string(pred_str, extend_lemma=extend_lemma, ctx=ctx)
        # ctx will never be null
        # ensure that pred_str is really a str
        pred_str = str(pred_str)
        pred = Pred.string_or_grammar_pred(pred_str)
        # use manual mapping whenever possible
        pred_str_search = pred_str if pred_str.endswith('_rel') else pred_str + '_rel'
        if pred_str_search in MWE_ERG_PRED_LEMMA:
            ss = PredSense.search_sense([MWE_ERG_PRED_LEMMA[pred_str_search]], pred.pos)
            return sorted(ss, key=lambda x: x.tagcount, reverse=True)
        else:
            return PredSense.search_pred(pred, extend_lemma)

    @staticmethod
    def search_pred(pred, auto_expand=True, ctx=None):
        ''' Retrieve suitable synsets for a given predicate, return a SynsetCollection '''
        # ensure not null ctx
        if ctx is None:
            with PredSense.wn.ctx() as ctx:
                return PredSense.search_pred(pred, auto_expand=auto_expand, ctx=ctx)
        # ctx will never be null
        if not pred:
            raise Exception("Predicate cannot be empty")
        # ignore some predicates
        if pred in PredSense.IGNORED_GPREDS:
            # don't map anything
            return SynsetCollection()
        pred_str = str(pred)
        if not pred_str.endswith('_rel'):
            pred_str += "_rel"
        if pred_str in PredSense.MANUAL_MAP:
            return PredSense.wn.get_synsets(PredSense.MANUAL_MAP[pred_str], ctx=ctx)
        elif pred.pos == 'x' and pred.sense == 'subord':
                return SynsetCollection()
        # elif (pred.pos == 'x' and pred.sense == 'deg') or pred.pos in 'pq':
        elif pred.pos and pred.pos in 'xpq':
            lemmata = [pred.lemma] if not auto_expand else list(PredSense.extend_lemma(pred.lemma))
            ssa = PredSense.search_sense(lemmata, 'a', ctx=ctx)
            ssr = PredSense.search_sense(lemmata, 'r', ctx=ctx)
            ssa = ssa.merge(ssr)
            return ssa

        lemmata = [pred.lemma] if not auto_expand else list(PredSense.extend_lemma(pred.lemma))
        pos = pred.pos

        ss = PredSense.search_sense(lemmata, pos, ctx=ctx)
        # hardcode: try to match noun & adj/v
        if not ss and auto_expand:
            getLogger().debug("Trying to change POS for lemmas: {}".format(lemmata))
            # hard code modal
            if pred.lemma in PredSense.MODAL_VERBS and pred.pos == 'v':
                ss = PredSense.search_sense(('modal',), 'a', ctx=ctx)
            elif pred.pos == 'a':
                ss = PredSense.search_sense(lemmata, 'r', ctx=ctx)
                if not ss:
                    pos = 'n'
                    ss = PredSense.search_sense(lemmata, pos, ctx=ctx)
            elif pred.pos == 'n':
                pos = 'a'
                ss = PredSense.search_sense(lemmata, pos, ctx=ctx)
        # Done
        return sorted(ss, key=lambda x: x.tagcount, reverse=True)
