#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ISF Gold Miner
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

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2016, ISF"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import argparse
import collections
import string
from collections import defaultdict as dd
from chirptext.leutile import header, TextReport, FileHelper, Counter
from chirptext.io import CSV
from puchikarui import Schema

from coolisf.gold_extract import *
from coolisf.model import Sentence, ChunkDB, LexItem, WordMRS, create_chunk_db
from coolisf import GrammarHub

########################################################################


is_nounep = lambda e : e and len(e.args) == 1 and 'ARG0' in e.args and e.pred.pos == 'n'


def mine_compoundnoun(text, mrs):
    compounds = []
    if mrs:
        noun_vars = set()
        eps = mrs.eps()
        # Find all noun first
        for ep in eps:
            if is_nounep(ep):
                noun_vars.add(ep.args['ARG0'])
        # find all compounds
        for ep in eps:
            if ep.pred.string == 'compound_rel':
                surface_str = text[ep.cfrom:ep.cto].lower().strip().strip(string.punctuation)
                print(surface_str[-1], surface_str)
                compounds.append((ep, surface_str))                
    return compounds


def mine_preds(args):
    r = TextReport('data/mining.txt')
    r.header('Pred mining')
    sid_gold_map = read_gold_tags()
    sentences = read_gold_mrs()
    r.print(len(sentences))

    # find all prepositions
    prepset = set()
    sentset = set()
    nounset = set()
    prepverbs = collections.Counter()
    prepverbsofto = collections.Counter()
    compounds = collections.Counter()
    for sent in sentences[:]:
        if sent.mrs:
            compounds.update([ x[1] for x in mine_compoundnoun(sent.text, sent.mrs[0].mrs()) ])
            for ep in sent.mrs[0].mrs().eps():
                if is_nounep(ep):
                    nounset.add(ep.pred.string)
                if ep.pred.pos == 'p':
                    prepset.add(ep.pred.lemma)
            preds = sent.mrs[0].preds()
            for pred in preds:
                if 'compound' in pred.label:
                    # r.writeline(sent.mrs[0].text)
                    # r.writeline('\n\n')
                    # r.writeline(sent.mrs[0].mrs())
                    sentset.add(sent.text)
                    
    # capture verb-preps
    for sent in sentences:
        if sent.mrs:
            for ep in sent.mrs[0].mrs().eps():
                if ep.pred.sense in ('of','to'):
                    prepverbsofto.update([ep.pred.string])
                elif ep.pred.sense in prepset:
                    prepverbs.update([ep.pred.string])

    r.header('Prep verb')
    for k,v in prepverbs.most_common():
        r.writeline('{} : {}'.format(k,v))
    
    r.header('Verb_of|to')    
    for k,v in prepverbsofto.most_common():
        r.writeline('{} : {}'.format(k,v))
    
    r.header('Prepositions')
    for p in prepset:
        r.writeline(p)

    r.writeline(nounset)

    r.header('Most common compounds')
    for k,v in compounds.most_common():
        r.writeline('{} : {}'.format(k,v))
        
    r.header('By alphabet')
    kvs = [(k, compounds[k]) for k in sorted(compounds.keys())]
    for k,v in kvs:
        r.writeline('{} : {}'.format(k,v))

    # print(sentset)
    # print(len(sentset))


def find_compound(args):
    raw_file = args.filepath + '.txt'
    mrs_file = args.filepath + '.mrs.txt'
    print("Looking for compounds from %s" % raw_file)
    from coolisf.gold_extract import read_ace_output
    sentences = read_ace_output(mrs_file)
    # look for compounds
    with open(args.filepath + '.mrs.compound_only.txt', 'w') as cpfile:
        for s in sentences:
            for mrs in s.mrs:
                if('compound' in mrs):
                    print("{}\t{}\t{}".format(s.sid, s.text, mrs))
                    cpfile.write('SENT: {}\n{}\n\n\n'.format(s.text, mrs))
    print("Done")


ghub = GrammarHub()
ERG = ghub.ERG


def parse_words(words, root='root_wn', ctx=None):
    words_iter = iter(words)
    total = len(words)
    word_lemmas = [word.lemma for word in words]
    idx = 0
    extra = []
    if root:
        extra.append('-r')
        extra.append(root)
    for parses in ERG.parse_many_iterative(word_lemmas, 20, extra):
        word = next(words_iter)
        print("Processing word {}/{}: {} (root = {})".format(idx + 1, total, word, root))
        if parses is not None and len(parses) > 0:
            word.flag = LexItem.PROCESSED
            matched = None
            for parse in parses:
                dmrs = parse.dmrs()
                if match(word, dmrs):
                    mrs = parse.mrs()
                    preds = dmrs.preds()
                    word.flag = LexItem.GOLD
                    ctx.parse.save(ParseMRS(raw=mrs.tostring(), wid=word.ID, preds=len(preds)))
                    matched = parse
            if matched is None:
                # there is no gold => store all
                # store parses
                for parse in parses:
                    mrs = parse.mrs()
                    dmrs = parse.dmrs()
                    preds = mrs.obj().eps()
                    for p in preds:
                        if p.pred.pos == 'u' and p.pred.sense == 'unknown':
                            word.flag = LexItem.UNKNOWN
                    ctx.parse.save(ParseMRS(raw=mrs.tostring(), wid=word.ID, preds=len(preds)))
            # save word
            ctx.word.save(word)
        else:
            # flag as error
            word.flag = LexItem.ERROR
            ctx.word.save(word)
        idx += 1


def parse_chunks(args):
    dbloc = FileHelper.abspath(args.dbloc)
    print("Chunk DB Path: {}".format(dbloc))
    db = ChunkDB(dbloc)
    # insert raw words if available
    if args.src is not None and os.path.isfile(args.src):
        create_chunk_db(args.src, db)
    # generate chunks
    if args.job == 'parse':
        with db.ctx() as ctx:
            # process all verbs first
            words = ctx.word.select("flag is NULL and pos = ?", ('v',))
            parse_words(words, root='root_frag', ctx=ctx)
            print("Non verb words")
            # and then the rest
            words = ctx.word.select("flag is NULL")
            parse_words(words, root='root_frag', ctx=ctx)

    elif args.job == 'error':
        # do something
        print("List error words")
        with db.ctx() as ctx:
            words = ctx.word.select("flag == ?", (LexItem.ERROR,))
            for idx, word in enumerate(words):
                print("Word {}/{}: {}".format(idx + 1, len(words), word))
        pass
    elif args.job == 'analyse':
        # do something
        print("Analysing")
        with db.ctx() as ctx:
            words = db.get_words(flag=LexItem.PROCESSED, pos=args.pos, limit=args.top, deep_select=False, ctx=ctx)
            for idx, word in enumerate(words):
                word.parses = db.get_parses(word, ctx=ctx)
                print("Word {}/{}: {}".format(idx + 1, len(words), word))
                analyse_word(word, ctx=ctx)
        pass
    else:
        print("What should I do (parse/error/analyse)? ")


def analyse_word(w, ctx):
    iw = w.to_isf()
    for p in iw:
        if match(w, p.dmrs()):
            print("[MATCHED] Word #{} ({}) => parse #{}".format(w.ID, w.lemma, p.ID))
            if p.ID:
                # delete the rest
                ctx.parse.delete("wid = ? AND ID != ?", (w.ID, p.ID))
                # flag word as gold
                if w.flag != LexItem.GOLD:
                    w.flag = LexItem.GOLD
                    ctx.word.save(w, columns=('flag',))
                    break
        if w.flag != LexItem.GOLD:
            preds = [p for p in p.dmrs().preds() if p != 'unknown' and p != 'udef_q']
            if len(preds) > 1 or 'compound' in preds:
                print("FOUND A COMPOUND")
                w.flag = LexItem.COMPOUND
                ctx.word.save(w, columns=('flag',))
                break


comp_nn = {'n'}
comp_an = {'a', 'n'}
comp_ne = {'named'}
nomv = {'nominalization', 'v'}


def analyse_compound(db, ctx, limit=None):
    constructions = dd(set)
    c = Counter()
    compounds = db.get_words(flag=LexItem.COMPOUND, pos=None, limit=limit, deep_select=False, ctx=ctx)
    ec = len(compounds)  # entry count
    for idx, word in enumerate(compounds):
        header("Processing {}/{}: {}".format(idx + 1, ec, word))
        db.get_parses(word, ctx)
        iw = word.to_isf()
        for parse in iw:
            d = parse.dmrs().obj()
            eps = [e for e in d.eps() if not is_ignorable(e.pred)]
            total = set()
            done = False
            for ep in eps:
                if ep.pred.pos and ep.pred.pos in 'nav':
                    total.add(ep.pred.pos)
                elif ep.pred.string != 'compound':
                    total.add(ep.pred.lemma)
                # compound > ignore
            if total == comp_nn and len(eps) > 1:
                print("Found COMP NN")
                db.flag(word, LexItem.COMP_NN, ctx)
                done = True
                break
            if total == comp_ne and len(eps) > 1:
                print("Found COMP NE")
                db.flag(word, LexItem.COMP_NE, ctx)
                done = True
                break
            elif total == comp_an:
                print("Found COMP AN")
                db.flag(word, LexItem.COMP_AN, ctx)
                done = True
                break
            elif total == nomv and len(eps) == 2:
                print("Found venom")
                db.flag(word, LexItem.NOM_VERB, ctx)
                done = True
                break
            elif len(eps) == 1 and eps[0].pred.pos and eps[0].pred.pos != word.pos:
                # mismatched
                print("Mismatched")
                word.flag = LexItem.MISMATCHED  # just note it,
            else:
                print("Dunno: constr={} | eps: {}".format(total, len(eps)))
                k = tuple(sorted(total))
                c.count(k)
                constructions[k].add(word.lemma)
                # print(parse.mrs())
                pass
        if done:
            continue
        elif word.flag == LexItem.MISMATCHED:
            print("Confirm MISMATCHED")
            db.flag(word, LexItem.MISMATCHED, ctx)
    # summarise
    print("All constructions")
    for k, l in constructions.items():
        header(str(k))
        print(l)
    for k, v in c.sorted_by_count():
        print(k, v)
    return True


def match(word, dmrs):
    eps = eps = [ep for ep in dmrs.obj().eps()]
    p = None
    if len(eps) == 1:
        p = eps[0].pred
    elif len(eps) == 2 and is_unk(eps[0]):
        p = eps[1].pred
    elif len(eps) == 3 and is_unk(eps[0]) and is_udef(eps[1]):
        p = eps[2].pred
    if p is not None:
        if p.pos == word.pos:
            if word.lemma == p.lemma:
                # exact matched
                return True
            elif p.sense:
                parts = p.sense.split('-')
                candidates = [p.lemma + ' ' + part for part in parts]
                candidates.append(p.lemma + '-' + '-'.join(parts))
                candidates.append(p.lemma + ' ' + ' '.join(parts))
                candidates.append(p.lemma + p.sense)  # daydream
                candidates.append(p.lemma + '-' + p.sense)
                candidates.append(p.lemma + ' ' + p.sense)  # look up
                candidates.append(p.lemma.replace('+', ' '))
                if word.lemma in candidates:
                    return True
            # not matched
    return False


def is_unk(ep):
    return ep == 'unknown_rel'


def is_udef(ep):
    return ep == 'udef_q'


def is_ignorable(ep):
    return ep in ('unknown_rel', 'udef_q', 'proper_q')


def validate_goldtags(args):
    r = TextReport('data/valgold.txt')
    from coolisf.gold_extract import read_gold_sentences
    sents = read_gold_sentences()
    for sent in sents:
        if len(sent) == 0:
            print("WARNING: {} is not parsed".format(sent.sid))
        for d in sent:
            extract_tags(r, d.dmrs(), sent.sid)


def extract_tags(report, d, sentid=None):
    d.json()  # call this to extract tags and sort them too
    for nodeid, tags in d.tags.items():
        ep = d.obj().ep(int(nodeid))
        tag_str = []
        for tag in tags:
            tag_str.append('\t'.join((str(tag[0].synsetid), tag[0].lemma, tag[1].upper())))
        cfrom, cto, surface = d.fix_tokenization(ep, d.parse.sent.text)
        report.print('\t'.join((str(sentid), str(cfrom), str(cto), '\t'.join(tag_str))))


def mine_stuff():
    print("Yay")


########################################################################

def main():
    ''' ISF Miner
    '''
    parser = argparse.ArgumentParser(description="ISF Miner")

    # Positional argument(s)
    task_parsers = parser.add_subparsers(help='Task to be done')

    mine_preds_task = task_parsers.add_parser('mine')
    mine_preds_task.set_defaults(func=mine_preds)

    parse_chunk_task = task_parsers.add_parser('chunks')
    parse_chunk_task.add_argument('--src', help="Source file")
    parse_chunk_task.add_argument('-t', '--top', help="Only process top K results", type=int)
    parse_chunk_task.add_argument('-p', '--pos', help="Filter words by POS")
    parse_chunk_task.add_argument('dbloc', help="Chunk database location", nargs="?", default="data/chunks.db")
    parse_chunk_task.add_argument('job', help='Job to be done')
    parse_chunk_task.set_defaults(func=parse_chunks)

    find_compound_task = task_parsers.add_parser('fcomp')
    find_compound_task.add_argument('filepath')
    find_compound_task.set_defaults(func=find_compound)

    # validate gold tags
    valgold_task = task_parsers.add_parser('vgold')
    valgold_task.set_defaults(func=validate_goldtags)

    # Optional argument(s)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    # Main script
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        # mine_preds()
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        args.func(args)


if __name__ == "__main__":
    main()
