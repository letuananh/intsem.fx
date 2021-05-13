# -*- coding: utf-8 -*-

"""
Lexical semantic manipulator
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging

from delphin.mrs.components import Pred

from texttaglib.chirptext import texttaglib as ttl
from yawlib import SynsetID


# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

SPECIAL_CHARS = """?!"'$-_&|.,;:“” """
# TODO: Move this to chirptext
PREPS = ['aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'excepting', 'excluding', 'following', 'for', 'from', 'in', 'inside', 'into', 'like', 'minus', 'near', 'of', 'off', 'on', 'onto', 'opposite', 'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'through', 'to', 'toward', 'towards', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within', 'without', 'that']
PREPS_PLUS = PREPS + ['a']


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------------------

class Lexsem(object):

    STRICT = 'strict'
    FLEXIBLE = 'flexible'
    ROBUST = 'robust'
    NAIVE = 'naive'
    MODES = [STRICT, FLEXIBLE, ROBUST, NAIVE]


def fix_tokenization(ep, sent_text=None):
    """ adjust cfrom, cto when a predicate is wrapped with special characters """
    cfrom = ep.cfrom
    cto = ep.cto
    surface = sent_text[cfrom:cto] if sent_text is not None else ''
    while len(surface) > 0 and surface[0] in SPECIAL_CHARS:
        surface = surface[1:]
        cfrom += 1
    while len(surface) > 0 and surface[-1] in SPECIAL_CHARS:
        surface = surface[:-1]
        cto -= 1
    return cfrom, cto, surface


def match(concept, ep, sent_text, mode=Lexsem.NAIVE, fix_token=True):
    """ Match concept (idv/MWE) with preds """
    if fix_token:
        cfrom, cto, surface = fix_tokenization(ep, sent_text)
    else:
        cfrom, cto, surface = ep.cfrom, ep.cto, sent_text[ep.cfrom:ep.cto] if sent_text is not None else ''
    if len(concept.tokens) == 1:
        pred_bits = list(ep.pred.lemma.split('+'))
        getLogger().debug("pred={} | plemma={}/bits={} | cfrom={} | cto={} | surface={} | concept={} | tokens={}".format(ep.pred, ep.pred.lemma, pred_bits, cfrom, cto, surface, concept, concept.tokens))
        w0 = concept.tokens[0]
        target_lemmas = (w0.text, concept.clemma)
        if mode == Lexsem.STRICT and ep.pred.pos == 'q' and ep.pred.type == Pred.GRAMMARPRED:
            return (ep.pred.pos in target_lemmas) and (w0.cfrom == cfrom) and (w0.cto == ep.cto)
        if w0.cfrom == cfrom or w0.cfrom == ep.cfrom:
            if w0.cto == cto or w0.cto == ep.cto:
                return True
            elif ep.pred.lemma in target_lemmas or surface in target_lemmas:
                return True
            elif len(pred_bits) == 2 and pred_bits[-1] in PREPS_PLUS and pred_bits[0] in (w0.text, concept.clemma):
                return True
        if concept.clemma in ('not', "n't") and ep.pred.lemma == 'neg' and w0.cto == cto:
            return True
    elif len(concept.tokens) > 1:
        # MWE
        tagged_words = tuple(w.text for w in concept.tokens)
        pred_bits = list(ep.pred.lemma.split('+'))
        # try to match using min-cfrom and max-cto first
        min_cfrom = concept.tokens[0].cfrom
        max_cto = concept.tokens[0].cto
        for w in concept.tokens[1:]:
            min_cfrom = min(min_cfrom, w.cfrom)
            max_cto = max(max_cto, w.cto)
            if cfrom == min_cfrom and cto == max_cto:
                return True
        # match by first word and lemma?
        if concept.tokens[0].cfrom == cfrom and concept.tokens[0].cto == cto and surface == concept.tokens[0].text:
            return True
        # match by pred.lemma and concept.tokens
        tagged_words = list(w.text for w in concept.tokens)
        pred_bits = list(ep.pred.lemma.split('+'))
        if tagged_words == pred_bits:
            return True
        # ignore the last preposition
        elif pred_bits[-1] in PREPS and tagged_words == pred_bits[:-1]:
            return True
        # match by ignoring the last part ...
        elif tagged_words == pred_bits[:-1]:
            getLogger().debug("Robust candidates: {} - {}".format(tagged_words, pred_bits))
            # TODO: mark this as ROBUST
            return True
        # no more to try ...
    else:
        raise Exception("Invalid (empty) concept")
    return False


def filter_concepts(concepts):
    # Ignore these non-senses
    # 00024073-r: not
    # 02604760-v: be
    # 02749904-v: be
    # 02655135-v: be
    # 02655135-v: be
    # 02603699-v: be
    # 02664769-v: be
    # 02620587-v: be
    # 77000091-n: what
    # 77000053-n: it
    # 00770437-v: have
    senses = []
    nonsenses = []
    for c in concepts:
        if c.tag in ('02604760-v', '00024073-r', '02749904-v', '02655135-v', '02603699-v', '02664769-v', '02620587-v', '77000091-n', '77000053-n', '00770437-v'):
            nonsenses.append(c)
        else:
            senses.append(c)
    return senses, nonsenses


def filter_bad_synsetids(concepts):
    good_concepts = []
    bad_concepts = []
    for c in concepts:
        valid_sid = SynsetID.from_string(c.tag, default=None)
        if valid_sid is None:
            getLogger().warning("{} is not a valid synset ID".format(c.tag))
            bad_concepts.append(c)
        else:
            good_concepts.append(c)
    return good_concepts, bad_concepts


def taggable_eps(eps, mode=Lexsem.ROBUST):
    """ Only tag real_preds, string_preds and some special gpreds:
             + named_rel
             + pron_rel
             + card_rel
    """
    if mode == Lexsem.STRICT:
        return [ep for ep in eps if ep.pred.type in (Pred.REALPRED, Pred.STRINGPRED) or ep.pred in ('named_rel', 'pron_rel', 'card_rel')]
    elif mode == Lexsem.NAIVE:
        return eps
    else:
        return [ep for ep in eps if ep.pred not in ('udef_q', 'pronoun_q', 'proper_q', 'def_implicit_q', 'free_relative_q', 'free_relative_ever_q', 'def_poss_q', 'number_q', 'every_q', 'which_q')]


def filter_small_senses(tagged):
    """ When a word is tagged with a MWE sense and an individual sense, ignore the individual one
    tagged is an instance of ttl.Sentence
    """
    to_be_removed = set()
    msw = tagged.msw()
    wcl = tagged.tcmap()
    for w in msw:
        maxed_c = wcl[w][0]
        ln = len(wcl[w][0].tokens)
        for c in wcl[w][1:]:
            if len(c.tokens) > ln:
                to_be_removed.add(maxed_c.cidx)
                # new max
                maxed_c = c
                ln = len(c.tokens)
            elif len(c.tokens) < ln:
                # remove this concept instead
                to_be_removed.add(c.cidx)
    # remove concepts
    removed = []
    for cid in to_be_removed:
        removed.append(tagged.pop_concept(cid))
    return removed


def import_shallow(isf_sent, *args, **kwargs):
    output = []
    for reading in isf_sent:
        if reading.dmrs() is not None:
            res = tag_gold(reading.dmrs(), isf_sent.shallow, isf_sent.text, *args, **kwargs)
            output.append(res)
    return output


def sort_eps(eps):
    # order: cfrom / cto / type (realpred first) / with_carg / quantifier
    eps.sort(key=lambda x: (x.cfrom, x.cto, 0 - x.pred.type, x.carg is None, x.pred.pos == 'q'))
    return eps


def tag_gold(dmrs, tagged_sent, sent_text, mode=Lexsem.ROBUST, no_small_sense=True, fix_token=True, no_nonsense=False):
    """ Use a ttl.Sentence to tag a DMRS
    Results (matched, not_matched) in which
        matched => (concept, ep.nodeid, ep.pred)
        not_matched => a list of concepts
    """
    # filter small senses (< MWE) out
    ignored = []
    if no_small_sense:
        ignored += filter_small_senses(tagged_sent)
    # filter (what I considered) non-senses out
    # [2018-02-19] Don't filter out concepts for now
    if no_nonsense:
        concepts, nonsenses = filter_concepts(tagged_sent.concepts)
        ignored += nonsenses
    else:
        concepts = tagged_sent.concepts
    # filter concepts with bad synsetIDs
    concepts, badconcepts = filter_bad_synsetids(concepts)
    ignored += badconcepts
    # idv_concepts = [c for c in concepts if len(c.words) == 1]
    eps = taggable_eps(dmrs.obj().eps(), mode=mode)
    sort_eps(eps)
    getLogger().debug("EPS: {}".format([(str(x.pred), x.pred.type) for x in eps]))
    matched_preds = []
    not_matched = []
    for c in concepts:
        matched = False
        for ep in eps:
            m = match(c, ep, sent_text, mode=mode, fix_token=fix_token)
            if m:
                matched_preds.append((c, ep.nodeid, ep.pred))
                dmrs.tag_node(ep.nodeid, c.tag, c.clemma, ttl.Tag.GOLD)
                eps.remove(ep)
                matched = True
                break
        if not matched:
            # tag concept not matched
            c.flag = ttl.Concept.NOT_MATCHED
            not_matched.append(c)
    if ignored:
        getLogger().debug("Ignored senses: {}".format(ignored))
    return matched_preds, not_matched, ignored
