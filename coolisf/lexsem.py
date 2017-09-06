# -*- coding: utf-8 -*-

'''
Lexical semantic manipulator

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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import logging
from collections import defaultdict as dd

from delphin.mrs.components import Pred

# from chirptext import header, Counter, TextReport
from chirptext.texttaglib import TagInfo, Concept
from yawlib import Synset


#-------------------------------------------------------------------------------
# CONFIGURATION
#-------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SPECIAL_CHARS = '''?!"'$-_&|.,;:'''
# TODO: Move this to chirptext
PREPS = ['aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'anti', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'concerning', 'considering', 'despite', 'down', 'during', 'except', 'excepting', 'excluding', 'following', 'for', 'from', 'in', 'inside', 'into', 'like', 'minus', 'near', 'of', 'off', 'on', 'onto', 'opposite', 'outside', 'over', 'past', 'per', 'plus', 'regarding', 'round', 'save', 'since', 'than', 'through', 'to', 'toward', 'towards', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within', 'without']
PREPS_PLUS = PREPS + ['a']


#-------------------------------------------------------------------------------
# FUNCTIONS
#-------------------------------------------------------------------------------

class Lexsem(object):

    STRICT = 'strict'
    FLEXIBLE = 'flexible'
    ROBUST = 'robust'


def fix_tokenization(ep, sent_text=None):
    ''' adjust cfrom, cto when a predicate is wrapped with special characters '''
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


def match(concept, ep, sent_text):
    ''' Match concept (idv/MWE) with preds '''
    cfrom, cto, surface = fix_tokenization(ep, sent_text)
    if len(concept.words) == 1:
        pred_bits = list(ep.pred.lemma.split('+'))
        # if concept.tag == '01554230-n':
        #     print(concept, ep.pred.lemma, pred_bits, cfrom, cto, surface)
        # ind concept
        w0 = concept.words[0]
        if w0.cfrom == cfrom or w0.cfrom == ep.cfrom:
            if w0.cto == cto or w0.cto == ep.cto:
                return True
            elif ep.pred.lemma == w0.label or surface == w0.label:
                return True
            elif len(pred_bits) == 2 and pred_bits[-1] in PREPS_PLUS and pred_bits[0] == w0.label:
                return True
    elif len(concept.words) > 1:
        tagged_words = tuple(w.label for w in concept.words)
        pred_bits = list(ep.pred.lemma.split('+'))
        # if concept.tag == '01554230-n':
        #     print("MWE", concept, ep.pred.lemma, pred_bits, cfrom, cto, surface, tagged_words)
        # MWE
        # try to match using min-cfrom and max-cto first
        min_cfrom = concept.words[0].cfrom
        max_cto = concept.words[0].cto
        for w in concept.words[1:]:
            min_cfrom = min(min_cfrom, w.cfrom)
            max_cto = max(max_cto, w.cto)
            if cfrom == min_cfrom and cto == max_cto:
                return True
        # match by first word and lemma?
        if concept.words[0].cfrom == cfrom and concept.words[0].cto == cto and surface == concept.words[0].label:
            return True
        # match by pred.lemma and concept.words
        tagged_words = list(w.label for w in concept.words)
        pred_bits = list(ep.pred.lemma.split('+'))
        if tagged_words == pred_bits:
            return True
        # ignore the last preposition
        elif pred_bits[-1] in PREPS and tagged_words == pred_bits[:-1]:
            return True
        # match by ignoring the last part ...
        elif tagged_words == pred_bits[:-1]:
            print(tagged_words, pred_bits)
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
    return [c for c in concepts if c.tag not in ('02604760-v', '00024073-r', '02749904-v', '02655135-v', '02603699-v', '02664769-v', '02620587-v', '77000091-n', '77000053-n', '00770437-v')]


def taggable_eps(eps):
    """ Only tag real_preds, string_preds and some special gpred:
             + named_rel
             + pron_rel
             + card_rel
    """
    return [ep for ep in eps if ep.pred.type in (Pred.REALPRED, Pred.STRINGPRED) or ep.pred in ('named_rel', 'pron_rel', 'card_rel')]


def filter_small_senses(tagged):
    ''' When a word is tagged with a MWE sense and an individual sense, ignore the individual one
    tagged is an instance of TaggedSentence
    '''
    to_be_removed = []
    msw = tagged.msw
    wcl = tagged.wclinks
    for w in msw:
        maxed_c = wcl[w][0]
        ln = len(wcl[w][0].words)
        for c in wcl[w][1:]:
            if len(c.words) > ln:
                to_be_removed.append(maxed_c.cid)
                # new max
                maxed_c = c
                ln = len(c.words)
            elif len(c.words) < ln:
                # remove this concept instead
                to_be_removed.append(c.cid)
    # remove concepts
    for cid in to_be_removed:
        if cid in tagged.concept_map:
            tagged.concept_map.pop(cid)


def tag_gold(dmrs, tagged_sent, sent_text, mode=Lexsem.ROBUST):
    ''' Use a TaggedSentence to tag a DMRS
    Results (matched, not_matched) in which
        matched => (concept, ep.nodeid, ep.pred)
        not_matched => a list of concepts
    '''
    # filter small senses (< MWE) out
    filter_small_senses(tagged_sent)
    # filter (what I considered) non-senses out
    concepts = filter_concepts(tagged_sent.concepts)
    # idv_concepts = [c for c in concepts if len(c.words) == 1]
    if mode == Lexsem.STRICT:
        eps = taggable_eps(dmrs.obj().eps())
    else:
        eps = dmrs.obj().eps()
    matched_preds = []
    not_matched = []
    for c in concepts:
        matched = False
        for ep in eps:
            m = match(c, ep, sent_text)
            if m:
                matched_preds.append((c, ep.nodeid, ep.pred))
                dmrs.tags[ep.nodeid].append((Synset(c.tag, lemma=c.clemma), TagInfo.GOLD))
                eps.remove(ep)
                matched = True
                break
        if not matched:
            # tag concept not matched
            c.flag = Concept.NOT_MATCHED
            not_matched.append(c)
    return matched_preds, not_matched
