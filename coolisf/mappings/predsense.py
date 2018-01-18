# -*- coding: utf-8 -*-

'''
ERG-Wordnet mapping

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
__copyright__ = "Copyright 2017, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import logging
from delphin.mrs.components import Pred

from yawlib import SynsetCollection
from yawlib.helpers import get_wn
from coolisf.mappings.mwemap import MWE_ERG_PRED_LEMMA


def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------

class PredSense(object):

    wn = get_wn()

    MODAL_VERBS = ('would', 'could', 'may', 'must', 'should', 'might', 'going+to', 'ought')

    REPLACE_TEMPLATES = [['-', ' '],
                         ['-', ''],
                         ['-', '+'],
                         ['_', ' '],
                         ['_', ''],
                         ['+', ' '],
                         ['+', '-'],
                         ['+', ''],
                         [' ', '-'],
                         [' ', '']]

    AUTO_EXTEND = {
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
        ('st', 'n'): (('saint', 'n'),),
        ('used+to', 'v'): (('used to', 'a'),),
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

    # [DONE]
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
        ''' Get a set of potential lemmas '''
        potential = set()
        potential.add(lemma)
        for rfrom, rto in PredSense.REPLACE_TEMPLATES:
            if rfrom in lemma:
                potential.add(lemma.replace(rfrom, rto))
        # add lower case
        potential.add(lemma.lower())
        potential.add(lemma.replace('+', ' '))
        potential.add(lemma.replace('+', '-'))
        potential.add(lemma.replace('-', ' '))
        potential.add(lemma.replace('-', '_'))
        potential.add(lemma.replace('_', ' '))
        potential.add(lemma.replace(' ', ''))
        # add +/-
        # potential.add(lemma + '+')
        # potential.add(lemma + '-')
        # negations & determiners
        if lemma.startswith('not+') or lemma.startswith('the+'):
            potential.add(lemma[4:])
        getLogger().debug("Potential for `{}': {}".format(lemma, potential))
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
        # ensure not null ctx
        if ctx is None:
            with PredSense.wn.ctx() as ctx:
                return PredSense.search_pred(pred, auto_expand=auto_expand, ctx=ctx)
        # ctx will never be null
        if not pred:
            raise Exception("Predicate cannot be empty")

        lemmata = [pred.lemma] if not auto_expand else list(PredSense.extend_lemma(pred.lemma))
        pos = pred.pos
        # FIXME
        # potentials = {(l, pos) for l in lemmata}
        # for l in lemmata:
        #     if (l, pos) in PredSense.AUTO_EXTEND:
        #         potentials.extend(PredSense.AUTO_EXTEND[(l, pos)])
        #     elif (l,) in PredSense.AUTO_EXTEND:
        #         potentials.extend((el, pos) for el in PredSense.AUTO_EXTEND[(l,)])

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
