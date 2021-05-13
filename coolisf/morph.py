# -*- coding: utf-8 -*-

"""
DMRS transforming utility
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging
from collections import defaultdict as dd

from texttaglib.chirptext import FileHelper

from coolisf.dao.ruledb import LexRuleDB
from coolisf.config import read_config
from coolisf.model import Sentence, Reading, DMRS

# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------


def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Classes
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
        """ Compound -> single pred """
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
        self.lemma = self.pred_lemma(lemma)
        self._graph = None
        self._adjacent_nodes = None
        self.adjacent = adjacent
        self.sign = self.head().predstr

    def head(self):
        return self.construction.head()

    def pred_lemma(self, text):
        return text.replace(' ', '+').replace('-', '+').replace("'", '')

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
                getLogger().debug("matching {} to {}: sub={}".format(node.predstr, self.sign, sub.to_dmrs()))
                if len(sub.nodes) == len(self.construction.nodes) and sub.top.to_graph() == self.graph:
                    if self.adjacent and self.adjacent_nodes != sub.adjacent_nodes():
                        getLogger().debug("Oh no, not adjacent - {} v.s {}".format(self.adjacent_nodes, sub.adjacent_nodes()))
                        continue
                    found.append(sub)
                else:
                    getLogger().debug("Not exactly matching")
        return found

    def apply(self, dmrs):
        matches = self.match(dmrs)
        if not matches:
            getLogger().debug("No subgraph matched for {}".format(self))
        for sub in matches:
            getLogger().debug("applying rule [lemma={}]: {} => {}".format(self.lemma, self.dmrs(), sub.to_dmrs()))
            self.transform(dmrs, sub)
        return dmrs

    def transform(self, dmrs, sub):
        """ subgraph -> pred """
        head = dmrs[sub.top.nodeid]
        # update lemma
        head.pred.lemma = self.lemma
        # udpate cfrom cto
        for n in sub.nodes:
            if n.predstr == 'compound':
                Integral.merge_compound(dmrs[n.nodeid])
            if n.cfrom < head.cfrom:
                head.cfrom = n.cfrom
            if n.cto > head.cto:
                head.cto = n.cto
        # delete nodes
        dmrs.delete(sub)

    def dmrs(self):
        return self.construction.to_dmrs()


class SimpleHeadedCompound(Compound):

    def __init__(self, construction, lemma, adjacent=True):
        super().__init__(construction, lemma, adjacent)
        head = self.head()
        if head is None:
            raise Exception("Invalid headed compound rule")
            # remove the unknown & RSTR by default
            to_del = set()
            for l in head.in_links:
                if l.is_rstr() or l.from_node.predstr == "unknown":
                    to_del.add(l.from_node)
            self.construction.delete(*to_del)

    def __eq__(self, other):
        if not other or not isinstance(other, Compound):
            return False
        else:
            return (self.construction, self.lemma, self.adjacent) == (other.construction, other.lemma, other.adjacent)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "SHComp(lemma={}, construction={})".format(repr(self.lemma), repr(self.construction.to_dmrs().to_mrs().tostring(False)))


class Transformer(object):

    def __init__(self, ruledb_path=None):
        # read rules
        self.rules = [self.get_guard_dog(),
                      self.get_green_tea(),
                      self.get_big_bad_wolf()]
        self.loaded = set()
        self.rule_map = dd(list)
        self.rule_cache = {}
        if not ruledb_path:
            # read from config file if not provided
            self.cfg = read_config()
            if self.cfg and 'lexrule_db' in self.cfg:
                ruledb_path = self.to_path(self.cfg['lexrule_db'])
        if ruledb_path and os.path.isfile(ruledb_path):
            getLogger().info("Lexrule DB location: {}".format(ruledb_path))
            self.rdb = LexRuleDB(ruledb_path)
        else:
            getLogger().warning("Rule DB could not be found. Only manual rules will be available.")
            self.rdb = None
            self.rule_signs = {}
        # sample rules
        self.add_rule(self.get_guard_dog())
        self.add_rule(self.get_green_tea())
        self.add_rule(self.get_big_bad_wolf())

    def to_path(self, path):
        return FileHelper.abspath(path.format(data_root=self.cfg['data_root']))

    def add_rule(self, rule):
        # getLogger().debug("Adding rule {}".format(rule.sign))
        self.rules.append(rule)
        self.rule_map[rule.sign].append(rule)

    def to_hcmp_rule(self, layout, lemma, adjacent=True):
        return SimpleHeadedCompound(layout, lemma, adjacent)

    def find_rules(self, nodes, limit=None):
        applicable_rules = []
        for node in nodes:
            applicable_rules.extend(self.rule_map[node.predstr])
        if self.rdb is None:
            return applicable_rules
        with self.rdb.ctx() as ctx:
            getLogger().debug("Searching for applicable rules for {} nodes: {}".format(len(nodes), nodes))
            ruleinfos = self.rdb.find_ruleinfo(nodes, limit=limit, ctx=None)
            getLogger().debug("Found {} rules".format(len(ruleinfos)))
            for ruleinfo in ruleinfos:
                ruleinfo = self.rdb.get_rule(ruleinfo.lid, ruleinfo.rid, ctx=ctx)
                if ruleinfo is not None:
                    lemma = ruleinfo.lemma.replace(' ', '+')
                    rule = self.to_hcmp_rule(ruleinfo[0].edit(), lemma)
                    if ruleinfo.ID not in self.loaded:
                        self.loaded.add(ruleinfo.ID)
                        self.add_rule(rule)
                    # getLogger().debug("{} vs {}".format(rule.sign, node.predstr))
                    applicable_rules.append(rule)
        getLogger().debug("Found {} rules in total".format(len(applicable_rules)))
        return applicable_rules

    def get_guard_dog(self):
        # [TODO] rules should not be hardcoded
        s = Reading("""[ TOP: h0 RELS: < [ compound<0:9> LBL: h1 ARG0: e4 [ e MOOD: indicative PERF: - PROG: - SF: prop TENSE: untensed ] ARG1: x6 [ x IND: + NUM: sg PERS: 3 ] ARG2: x5 [ x IND: + PT: notpro ] ]
          [ udef_q<0:5> LBL: h2 ARG0: x5 RSTR: h7 ]
          [ _guard_n_1<0:5> LBL: h3 ARG0: x5 ]
          [ _dog_n_1<6:9> LBL: h1 ARG0: x6 ] >
  HCONS: < h0 qeq h1 h7 qeq h3 > ]""").edit()
        return Compound(s, "guard+dog", adjacent=True)

    def get_green_tea(self):
        s = Reading("""[ TOP: h0
  INDEX: e2 [ e SF: prop-or-ques ]
  RELS: < [ _green_a_2<0:5> LBL: h8 ARG0: e9 [ e SF: prop TENSE: untensed MOOD: indicative PROG: bool PERF: - ] ARG1: x4 ]
          [ _tea_n_1<6:9> LBL: h8 ARG0: x4 ] >
  HCONS: < h0 qeq h8 > ]""").edit()
        return Compound(s, "green+tea", adjacent=True)

    def get_big_bad_wolf(self):
        s = Reading("""[ TOP: h0
  RELS: < [ _big_a_1<0:3> LBL: h1 ARG0: e2 [ e MOOD: indicative PERF: - PROG: bool SF: prop TENSE: untensed ] ARG1: x4 [ x IND: + NUM: sg PERS: 3 ] ]
          [ _bad_a_at<4:7> LBL: h1 ARG0: e3 [ e SF: prop ] ARG1: x4 ]
          [ _wolf_n_1<8:12> LBL: h1 ARG0: x4 ] >
  HCONS: < h0 qeq h1 > ]""").edit()
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
                    if arg1 and Integral.is_named(arg1):
                        # collapse compound
                        Integral.collapse(arg1)
            getLogger().debug("locating rules for nodes {}".format(target.nodes))
            applicable_rules = self.find_rules(target.nodes)
            # apply MWE rules
            getLogger().debug("There are {} applicable rules for {}".format(len(applicable_rules), target.nodes))
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
