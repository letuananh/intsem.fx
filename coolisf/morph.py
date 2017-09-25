# -*- coding: utf-8 -*-

'''
DMRS transforming utility
Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, intsem.fx"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import logging
from collections import defaultdict as dd

from coolisf.mappings.optimus import rules as optimus_rules
from coolisf.model import Sentence, Reading, DMRS, ChunkDB

# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
DATA_FOLDER = os.path.abspath(os.path.expanduser('./data'))
CHUNKDB = os.path.join(DATA_FOLDER, "chunks.db")


# -------------------------------------------------------------------------------
# CLASSES
# -------------------------------------------------------------------------------

class Integral(object):

    @staticmethod
    def is_named(node, verified=None):
        if verified is None:
            verified = set()
        if node.nodeid in verified:
            return True
        elif node.pred.predstr == "named":
            verified.add(node.nodeid)
            in_comps = [n.from_node for n in node.in_links if n.from_node.predstr == 'compound']
            # all in compound must be checked as well
            for comp in in_comps:
                if not Integral.is_named(comp, verified=verified):
                    return False
            return True
        elif node.pred.predstr == "compound":
            verified.add(node.nodeid)
            # check ARG1, ARG2 and all in compounds
            arg1 = node['ARG1']
            arg2 = node['ARG2']
            if arg1 and not Integral.is_named(arg1, verified):
                return False
            if arg2 and not Integral.is_named(arg2, verified):
                return False
            in_comps = [n.from_node for n in node.in_links if n.from_node.predstr == 'compound']
            for comp in in_comps:
                if not Integral.is_named(comp, verified=verified):
                    return False
            return True
        else:
            return False

    @staticmethod
    def merge_compound(comp_node, update_text=False):
        ''' Compound -> single pred '''
        arg1 = comp_node['ARG1']
        arg2 = comp_node['ARG2']
        if arg1.cto == comp_node.cto and arg2.cfrom == comp_node.cfrom and arg2.cto + 1 == arg1.cfrom:
            # it's possible to use cfrom/cto from compound
            arg1.cfrom = comp_node.cfrom
            arg1.cto = comp_node.cto
        if update_text:
            # merge lemma
            if arg1.predstr == 'named' and arg2.predstr == 'named':
                # merge carg
                arg1.carg = " ".join((arg2.carg, arg1.carg))
            else:
                arg1.pred = "+".join((arg2.lemma, arg1.lemma))

    @staticmethod
    def collapse(arg1):
        comps = sorted(Integral.get_comps(arg1), key=lambda x: -x['ARG2'].cfrom)
        if not comps:
            return True  # No need to do anything
        else:
            for comp in comps:
                arg2 = comp['ARG2']
                if arg2.predstr != 'named':
                    return False  # cannot be collapsed
                if Integral.collapse(arg2):
                    Integral.merge_compound(comp, update_text=True)
                    # delete arg2 & comp
                    to_del = [l.from_nodeid for l in arg2.in_links]
                    arg1.dmrs.delete(*to_del)
                    arg1.dmrs.delete(arg2)
        return True

    @staticmethod
    def get_comps(a_node):
        if not a_node:
            return None
        else:
            return [l.from_node for l in a_node.in_links if l.from_node.predstr == 'compound' and l.rargname == 'ARG1']


class Compound(object):

    def __init__(self, construction, lemma, adjacent=False):
        self.construction = construction
        self.lemma = lemma
        self._graph = None
        self._adjacent_nodes = None
        self.adjacent = adjacent
        self.sign = self.head().predstr

    def head(self):
        if self.construction.top.predstr == "unknown":
            return self.construction.top["ARG"]
        else:
            return self.construction.top

    @property
    def graph(self):
        if self._graph is None:
            self._graph = self.head().to_graph()
        return self._graph

    @property
    def adjacent_nodes(self):
        if self._adjacent_nodes is None:
            self._adjacent_nodes = self.construction.adjacent_nodes()
        return self._adjacent_nodes

    def match(self, dmrs):
        found = []
        for node in dmrs.nodes:
            if node.predstr == self.sign:
                sub = dmrs.subgraph(node, constraints=self.construction)
                if sub.top.to_graph() == self.graph:
                    if self.adjacent:
                        if self.adjacent_nodes != sub.adjacent_nodes():
                            continue
                    found.append(sub)
        return found

    def apply(self, dmrs):
        for sub in self.match(dmrs):
            self.transform(dmrs, sub)
        return dmrs

    def transform(self, dmrs, sub):
        head = dmrs[sub.top.nodeid]
        # update lemma
        head.pred.lemma = self.lemma
        # udpate cfrom cto
        for n in sub.nodes:
            if n.predstr == 'compound':
                Integral.merge_compound(dmrs[n.nodeid])
        # delete nodes
        dmrs.delete(sub)

    def dmrs(self):
        return self.construction.to_dmrs()


class NounNounCompound(Compound):

    def __init__(self, construction, lemma, adjacent=True):
        super().__init__(construction, lemma, adjacent)
        head = self.head()
        if head is None or head.rppos != 'n':
            raise Exception("Invalid noun-noun compound rule")
        # remove the unknown & RSTR by default
        to_del = set()
        for l in head.in_links:
            if l.is_rstr() or l.from_node.predstr == "unknown":
                to_del.add(l.from_node)
        self.construction.delete(*to_del)


class RuleDB(ChunkDB):

    def __init__(self, dbpath):
        super().__init__(dbpath)

    def get_rules(self, word):
        lemma = word.lemma.replace(' ', '+').replace('-', '+')
        iword = word.to_isf()
        rules = [NounNounCompound(p.edit(), lemma) for p in iword]
        return rules

    def get_rule(self, wid, pid, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.get_rule(wid, pid, ctx=ctx)
        word = ctx.word.by_id(wid)
        parse = ctx.parse.by_id(pid)
        if word is not None and parse is not None:
            word.parses.append()
        else:
            logger.warning("Rule {}/{} could not be loaded. Make sure that rule db file exists.".format(wid, pid))
            return None
        try:
            r = self.get_rules(word)
            return r[0]
        except:
            logger.exception("Cannot load rule")
            return None


class Transformer(object):

    def __init__(self):
        # read rules
        self.rules = [self.get_guard_dog(),
                      self.get_green_tea(),
                      self.get_big_bad_wolf()]
        self.rule_map = dd(list)
        if os.path.isfile(CHUNKDB):
            self.rdb = RuleDB(CHUNKDB)
            self.rule_signs = optimus_rules
        else:
            logger.warning("Rule DB could not be found. Only manual rules will be available.")
            self.rdb = None
            self.rule_signs = {}
        # sample rules
        self.add_rule(self.get_guard_dog())
        self.add_rule(self.get_green_tea())
        self.add_rule(self.get_big_bad_wolf())

    def add_rule(self, rule):
        self.rules.append(rule)
        self.rule_map[rule.sign].append(rule)

    def find_rules(self, nodes):
        applicable_rules = []
        # use manual rules
        # [TODO] Fix this
        if self.rdb is None:
            for node in nodes:
                applicable_rules.extend(self.rule_map[node.predstr])
            return applicable_rules
        with self.rdb.ctx() as ctx:
            for node in nodes:
                if node.predstr in self.rule_map:
                    applicable_rules.extend(self.rule_map[node.predstr])
                elif node.predstr in self.rule_signs:
                    # print(node.predstr, "Found rule: ", self.rule_signs[node.predstr])
                    for wid, pid in self.rule_signs[node.predstr]:
                        rule = self.rdb.get_rule(wid, pid, ctx)
                        if rule is not None:
                            self.add_rule(rule)
                            applicable_rules.append(rule)
                else:
                    # something else
                    continue
        return applicable_rules

    def get_guard_dog(self):
        # [TODO] rules should not be hardcoded
        s = Reading('''[ TOP: h0 RELS: < [ compound<0:9> LBL: h1 ARG0: e4 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: x6 [ x IND: + NUM: sg PERS: 3 ] ARG2: x5 [ x IND: + PT: notpro ] ]
          [ udef_q<0:5> LBL: h2 ARG0: x5 RSTR: h7 ]
          [ _guard_n_1<0:5> LBL: h3 ARG0: x5 ]
          [ _dog_n_1<6:9> LBL: h1 ARG0: x6 ] >
  HCONS: < h0 qeq h1 h7 qeq h3 > ]''').edit()
        return Compound(s, "guard+dog", adjacent=True)

    def get_green_tea(self):
        s = Reading('''[ TOP: h0
  INDEX: e2 [ e SF: prop-or-ques ]
  RELS: < [ _green_a_2<0:5> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x4 ]
          [ _tea_n_1<6:9> LBL: h8 ARG0: x4 ] >
  HCONS: < h0 qeq h8 > ]''').edit()
        return Compound(s, "green+tea", adjacent=True)

    def get_big_bad_wolf(self):
        s = Reading('''[ TOP: h0
  RELS: < [ _big_a_1<0:3> LBL: h1 ARG0: e2 [ e MOOD: indicative PERF: - PROG: bool SF: prop TENSE: untensed ] ARG1: x4 [ x IND: + NUM: sg PERS: 3 ] ]
          [ _bad_a_at<4:7> LBL: h1 ARG0: e3 [ e SF: prop ] ARG1: x4 ]
          [ _wolf_n_1<8:12> LBL: h1 ARG0: x4 ] >
  HCONS: < h0 qeq h1 > ]''').edit()
        return Compound(s, "big+bad+wolf", adjacent=True)

    def process(self, target):
        if isinstance(target, Reading) or isinstance(target, DMRS):
            return self.process(target.edit())
        else:
            # target is a DMRSEditor
            # collapse named compound
            for node in target.nodes:
                if node.predstr == "compound":
                    arg1 = node['ARG1']
                    if Integral.is_named(arg1):
                        # collapse compound
                        Integral.collapse(arg1)
            applicable_rules = self.find_rules(target.nodes)
            # apply MWE rules
            for rule in applicable_rules:
                rule.apply(target)
            return target

    def apply(self, target):
        if isinstance(target, Sentence):
            for parse in target:
                self.apply(parse)
                return target
        else:
            result = self.process(target)
            result.save()
            return target