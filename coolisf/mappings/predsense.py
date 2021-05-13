# -*- coding: utf-8 -*-

"""
ERG-Wordnet mapping
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging
import copy
from itertools import chain
from collections import defaultdict as dd
from delphin.mrs.components import Pred

from yawlib import SynsetCollection
from yawlib.helpers import get_wn
from coolisf.common import ptpos_to_wn, get_ep_lemma
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
                      'reason_n_rel', 'proper_q_rel')
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
    MANUAL_MAP = {'neg_rel': ('00024073-r',),
                  '_no_a_1_rel': ('00024356-r',),
                  'no_q_rel': ('02268485-a',),
                  'little-few_a_rel': ('01552885-a', '01554510-a'),
                  'more_comp_rel': ('00099341-r',),
                  '_more_x_comp_rel': ('00099341-r',),
                  '_more_a_1_rel': ('00099712-r',),
                  '_more+than_p_rel': ('01555133-a',),
                  'superl_rel': ('00111609-r',),
                  'the+most_q_rel': ('01555732-a',),
                  '_most_q_rel': ('01557120-a',),
                  'be_v_id_rel': ('02604760-v', ' 02664769-v', '02445925-v', '02616386-v'),
                  'be_v_there_rel': ('02749904-v', '02603699-v', '02655135-v')}

    @staticmethod
    def extend_lemma(lemma):
        """ Get a set of potential lemmas """
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
    search_cache = dd()

    @staticmethod
    def search_sense(lemmata, pos=None, ctx=None):
        search_key = (tuple(lemmata), pos)
        if search_key in PredSense.search_cache:
            return copy.deepcopy(PredSense.search_cache[search_key])
        if ctx is None:
            with PredSense.wn.ctx() as ctx:
                return PredSense.search_sense(lemmata, pos=pos, ctx=ctx)
        # ctx is ensured to be not null
        """ Return a SynsetCollection """
        if pos and pos in ('x', 'p'):
            pos = None
        potential = SynsetCollection()
        getLogger().debug("search sense lemmas={} (pos={})".format(lemmata, pos))
        for lemma in lemmata:
            synsets = PredSense.wn.search(lemma, pos=pos, ctx=ctx)
            getLogger().debug("search_sense: {} (pos={}): {}".format(lemma, pos, synsets))
            for synset in synsets:
                if synset.ID not in potential:
                    synset.lemma = lemma
                    potential.add(synset)
        PredSense.search_cache[search_key] = potential
        return potential

    # alias
    @staticmethod
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
        # if this is a known preds
        if pred_str_search in MWE_ERG_PRED_LEMMA:
            ss = PredSense.search_sense([MWE_ERG_PRED_LEMMA[pred_str_search]], pred.pos)
            if ss:
                return sorted(ss, key=lambda x: x.tagcount, reverse=True)
        return PredSense.search_pred(pred, extend_lemma)

    @staticmethod
    def get_wn_pos(ep, **kwargs):
        candidates = list(PredSense.search_ep(ep, **kwargs))
        if candidates:
            return candidates[0].ID.pos
        else:
            return ep.pred.pos if ep.pred.pos and ep.pred.pos in 'nvar' else 'x'

    @staticmethod
    def search_ep(ep, extend_lemma=True, ctx=None):
        candidates = None
        pred_str = str(ep.pred)
        if not pred_str.endswith('_rel'):
            pred_str += "_rel"
        getLogger().debug("search_ep {} | pred={}".format(ep, pred_str))
        if pred_str in PredSense.MANUAL_MAP:
            return PredSense.wn.get_synsets(PredSense.MANUAL_MAP[pred_str], ctx=ctx)
        elif ep.pred.type == Pred.GRAMMARPRED and ep.carg:
            lemmas = PredSense.extend_lemma(ep.carg) if extend_lemma else (ep.cargs,)
            pos = None
            arg0 = ep.args['ARG0'] if 'ARG0' in ep.args else ''
            if arg0.startswith('e'):
                pos = 'a'
            elif arg0.startswith('i') or arg0.startswith('x'):
                pos = 'n'
            candidates = PredSense.search_sense(lemmas, pos=pos, ctx=ctx)
            getLogger().debug("Candidate for {}: {}".format(ep.pred.string, candidates))
        elif ep.pred.pos == 'a' and 'ARG1' in ep.args:
            if extend_lemma:
                lemmas = list(chain(PredSense.extend_lemma(ep.pred.lemma), PredSense.extend_lemma(ep.pred.lemma + 'ly')))
            else:
                lemmas = (ep.pred.lemma, ep.pred.lemma + 'ly')
            arg1 = ep.args['ARG1']
            # try to guess POS first
            if arg1.startswith('h') or arg1.startswith('e'):
                pos = 'r'
            else:
                pos = 'a'
            candidates = PredSense.search_sense(lemmas, pos=pos, ctx=ctx)
            if candidates:
                return candidates
            else:
                # change to the other
                old_pos = pos
                pos = 'r' if pos != 'r' else 'a'
                getLogger().debug("Not found {}, change POS {} -> {}".format(lemmas, old_pos, pos))
                candidates = PredSense.search_sense(lemmas, pos=pos, ctx=ctx)
                getLogger().debug("Candidate for {}: {}".format(ep.pred.string, candidates))
        else:
            candidates = PredSense.search_pred_string(ep.pred.string, ctx=ctx)
            getLogger().debug("Candidates for [{} [CARG '{}']]: {}".format(ep.pred.string, ep.carg, [(c, c.lemmas) for c in candidates]))
        if candidates:
            return candidates
        # try to search by known lemmas
        if pred_str in MWE_ERG_PRED_LEMMA:
            ss = PredSense.search_sense([MWE_ERG_PRED_LEMMA[pred_str]], ep.pred.pos)
            if ss:
                sorted(ss, key=lambda x: x.tagcount, reverse=True)
        # search by preds
        return PredSense.search_pred(ep.pred, auto_expand=extend_lemma, ctx=ctx)

    @staticmethod
    def search_pred(pred, auto_expand=True, ctx=None):
        """ Retrieve suitable synsets for a given predicate, return a SynsetCollection """
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
        # don't map modal verbs
        if pred.lemma in PredSense.MODAL_VERBS and pred.pos == 'v' and pred.sense == 'modal':
            #    ss = PredSense.search_sense(('modal',), 'a', ctx=ctx)
            return SynsetCollection()
        pred_str = str(pred)
        if not pred_str.endswith('_rel'):
            pred_str += "_rel"
        if pred_str in PredSense.MANUAL_MAP:
            return PredSense.wn.get_synsets(PredSense.MANUAL_MAP[pred_str], ctx=ctx)
        elif pred.pos == 'x' and pred.sense == 'subord':
                return SynsetCollection()
        elif pred.pos == 'u' and pred.sense == 'unknown' and '/' in pred.lemma:
            # unknown pred handling
            unk_lemma, unk_pos = pred.lemma.split('/')
            pos = ptpos_to_wn(unk_pos)
            getLogger().debug("Unknown | lemma: {} | unk_pos: {} | pos: {}".format(unk_lemma, unk_pos, pos))
            lemmata = [unk_lemma] if not auto_expand else list(PredSense.extend_lemma(unk_lemma))
        # elif (pred.pos == 'x' and pred.sense == 'deg') or pred.pos in 'pq':
        elif pred.pos and pred.pos in 'xpq':
            lemmata = [pred.lemma] if not auto_expand else list(PredSense.extend_lemma(pred.lemma))
            ssa = PredSense.search_sense(lemmata, 'a', ctx=ctx)
            ssr = PredSense.search_sense(lemmata, 'r', ctx=ctx)
            ssa = ssa.merge(ssr)
            return ssa
        else:
            lemmata = [pred.lemma] if not auto_expand else list(PredSense.extend_lemma(pred.lemma))
            pos = pred.pos
        if pred.type == Pred.GRAMMARPRED:
            # at this point, if it's not a known gpred, kill it
            return SynsetCollection()
        ss = PredSense.search_sense(lemmata, pos, ctx=ctx)
        # hardcode: try to match noun & adj/v
        if not ss and auto_expand:
            getLogger().debug("Trying to change POS for lemmas: {}".format(lemmata))
            # hard code modal
            if pred.pos == 'a':
                ss = PredSense.search_sense(lemmata, 'r', ctx=ctx)
                if not ss:
                    pos = 'n'
                    ss = PredSense.search_sense(lemmata, pos, ctx=ctx)
            elif pred.pos == 'n':
                pos = 'a'
                ss = PredSense.search_sense(lemmata, pos, ctx=ctx)
        # Done
        ss.synsets.sort(key=lambda x: x.tagcount, reverse=True)
        # return sorted(ss.synsets, key=lambda x: x.tagcount, reverse=True)
        return ss
