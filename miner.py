#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ISF Gold Miner
Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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

import argparse
import logging

from yawlib import YLConfig
from yawlib.omwsql import OMWSQL

from coolisf import GrammarHub
from coolisf.model import LexUnit, Reading
from coolisf.dao.ruledb import parse_lexunit
from coolisf.morph import LEXRULES_DB, LexRuleDB


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

UNK_DOCS = {'n': 'unk_noun', 'v': 'unk_verb', 'a': 'unk_adj', 'r': 'unk_adv', 'x': 'unk_other'}


def getLogger():
    return logging.getLogger(__name__)


# ---------------------------------------------------------
# Funtions
# ---------------------------------------------------------

def mark_unknown_words(lu, ctx):
    for reading in lu:
        if contains_unknown_words(reading.dmrs().layout):
            # flag this lu as unknown word
            print("Flag {} with LexUnit.UNKNOWN".format(lu))
            ctx.schema.flag(lu, LexUnit.UNKNOWN, ctx=ctx)
            # move to correct document
            doc_name = UNK_DOCS[lu.pos] if lu.pos in UNK_DOCS else UNK_DOCS['x']
            lu.parses.docID = ctx.schema.get_doc(doc_name, ctx=ctx).ID
            ctx.sentence.save(lu.parses, columns=('docID',))
            return True
        return False


def contains_unknown_words(layout):
    for node in layout.nodes:
        if node.rppos == 'u' and node.rpsense == 'unknown':
            return True
    return False


def mark_compounds(lu, ctx):
    for reading in lu:
        is_compound = False
        for node in reading.dmrs().layout.nodes:
            if node.predstr == 'compound':
                is_compound = True
                continue
            else:
                break
    # flag this lu as a compound
    if is_compound:
        ctx.schema.flag(lu, LexUnit.COMPOUND, ctx=ctx)
    return is_compound


def add_comment(rdb, wn, limit=None):
    with rdb.ctx() as ctx, wn.ctx() as wnctx:
        q = 'sentid IN (SELECT ID from sentence WHERE comment IS NULL)'
        lus = ctx.lexunit.select(q, limit=limit)
        for lu in lus:
            ss = wn.get_synset(lu.synsetid, ctx=wnctx)
            if ss.exes:
                cmt = "{}: {} | \nExes: {}".format(ss.sid, ss.definition, ', '.join(ss.exes))
            else:
                cmt = "{}: {}".format(ss.sid, ss.definition)
            rdb.note_sentence(lu.sentid, cmt, ctx=ctx)


def is_noun_compound(layout):
    ''' Check if a particular DMRS is a noun/noun phrase '''
    head = layout.head() if layout is not None else None
    return layout is not None and head is not None and (head.pred.pos == 'n' or head.predstr == 'nominalization' or head.predstr == 'person')


def mark_noun_concept(lu, ctx):
    if lu.pos != 'n':
        return False
    to_remove = []
    for r in lu:
        if not is_noun_compound(r.dmrs().layout):
            r.mode = Reading.INACTIVE
            to_remove.append(r)
        else:
            r.mode = Reading.ACTIVE
            ctx.reading.save(r, columns=('mode',))
    if len(to_remove) < len(lu):
        # there's at least 1 active reading => mark this as a noun
        ctx.schema.flag(lu, LexUnit.NOUN, ctx=ctx)
    else:
        ctx.schema.flag(lu, LexUnit.MISMATCHED, ctx=ctx)
    return True


def activate(*readings, ctx):
    for reading in readings:
        reading.mode = Reading.ACTIVE
        ctx.reading.save(reading, columns=('mode',))


def deactivate(*readings, ctx):
    for reading in readings:
        reading.mode = Reading.INACTIVE
        ctx.reading.save(reading, columns=('mode',))


# ---------------------------------------------------------
# Tasks
# ---------------------------------------------------------

class RuleGenerator(object):

    ghub = GrammarHub()
    wn = OMWSQL(YLConfig.OMW_DB)

    def __init__(self, lang='eng', grm=None):
        self.grm = self.ghub.ERG if grm is None else grm
        self.lang = lang

    def process(self, lu):
        print("Processing: {}".format(lu))
        return parse_lexunit(lu, self.grm)

    def gen_ruledb(self, args):
        rdb = LexRuleDB(args.dbloc)
        # read wordnets
        query = """SELECT word.lemma, sense.synset, word.pos FROM sense LEFT JOIN word ON sense.wordid = word.wordid WHERE sense.lang = ?"""
        senses = self.wn.ctx().select(query, (self.lang,))
        lexunits = (LexUnit(lemma=s['lemma'], pos=s['pos'], synsetid=s['synset']) for s in senses)
        with rdb.ctx() as ctx:
            # don't parse => faster
            # rdb.generate_rules(lexunits, lambda x: self.process(x, self.ghub.ERG), ctx=ctx)
            rdb.generate_rules(lexunits, None, ctx=ctx)

    def parse_ruledb(self, args):
        rdb = LexRuleDB(args.dbloc)
        with rdb.ctx() as ctx:
            unparsed = ctx.lexunit.select('flag IS NULL')
            for rule in unparsed:
                print("Parsing {}".format(rule))
                rdb.parse_rule(rule, self.process, ctx=ctx)

    def analyse_ruledb(self, args):
        rdb = LexRuleDB(args.dbloc)
        with rdb.ctx() as ctx:
            lexunits = rdb.find_lexunits(flag=LexUnit.PROCESSED, limit=args.n, lazy=False, ctx=ctx)
            for lu in lexunits:
                rdb.get_lexunit(lu, ctx=ctx)
                if not mark_unknown_words(lu, ctx):
                    # this lexunit is a known word
                    if mark_compounds(lu, ctx):
                        print("Found a compound: {}".format(lu))
                    pass

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------


def main():
    ''' ISF Miner
    '''
    parser = argparse.ArgumentParser(description="ISF Miner", add_help=False)
    parser.set_defaults(func=None)

    # Positional argument(s)
    task_parsers = parser.add_subparsers(help='Task to be done')

    ruledb_task = task_parsers.add_parser('ruledb', add_help=False)
    ruledb_task.add_argument('--dbloc', default=LEXRULES_DB)
    ruledb_jobs = ruledb_task.add_subparsers(help='Job to perform on rule DB')
    # generate DB
    gen_job = ruledb_jobs.add_parser('gen', parents=[ruledb_task])
    gen_job.set_defaults(func=RuleGenerator().gen_ruledb)
    # parse unparsed lexunits
    parse_job = ruledb_jobs.add_parser('parse', parents=[ruledb_task])
    parse_job.set_defaults(func=RuleGenerator().parse_ruledb)
    # analyse parsed lexunits
    analyse_job = ruledb_jobs.add_parser('analyse', parents=[ruledb_task])
    analyse_job.add_argument('-n', help="Limit to top n records", default=None)
    analyse_job.set_defaults(func=RuleGenerator().analyse_ruledb)
    # Main script
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
