#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script for processing gold datasets

Latest version can be found at https://github.com/letuananh/intsem.fx

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
'''

# Copyright (c) 2018, Le Tuan Anh <tuananh.ke@gmail.com>
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
from collections import defaultdict as dd

from chirptext import TextReport, Counter
from chirptext.anhxa import DataObject as DO
from chirptext.cli import CLIApp, setup_logging
from chirptext import texttaglib as ttl

from coolisf.lexsem import Lexsem, import_shallow, sort_eps
from coolisf.gold_extract import read_gold_mrs
from coolisf.model import Document
from coolisf.mappings import PredSense

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

UPDATE_QUERY = """
UPDATE sent SET sent = '{ntext}'
WHERE           sent = '{otext}'
                AND sid = '{sid}';"""

setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def patch_gold_sid(sents):
    ''' patch TSDB ident to NTU format '''
    for idx, s in enumerate(sents):
        s.ident = idx + 10000


def fix_gold(cli, args):
    ''' Generate SQLite script to patch typo in IMI's data '''
    sents = read_gold_mrs()
    patch_gold_sid(sents)
    print("Gold sentences: {}".format(len(sents)))
    doc = ttl.Document('gold', path='data').read()
    print("TTL sentences: {}".format(len(doc)))
    patches = []
    for s in sents:
        # print("Checking #{}".format(s.ident))
        tagged = doc.get(int(s.ident))
        if tagged.text != s.text:
            new_text = s.text.replace("'", "''")
            old_text = tagged.text.replace("'", "''")
            patch = UPDATE_QUERY.format(ntext=new_text, sid=s.ident, otext=old_text)
            patches.append(patch)
    # generate patch
    if patches:
        with TextReport(args.output) as outfile:
            for patch in patches:
                outfile.print(patch)
        print("-- Patch has been written to {}".format(outfile.path))
    else:
        print("Nothing to patch")


def map_all(cli, args):
    grid = [
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, output="{}_naive.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, fixtoken=True, output="{}_naive_ft.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, noss=True, output="{}_naive_noss.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, noss=True, fixtoken=True, output="{}_naive_noss_ft.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.ROBUST, noss=True, fixtoken=True, output="{}_robust.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.STRICT, noss=True, fixtoken=True, output="{}_strict.txt".format(args.prefix)),
    ]
    results = []
    yes = {'tex': 'Y', 'org': 'X'}
    for prof in grid:
        output = map_predsense(cli, prof)
        results.append(output)
    for (prof, (total_concepts, total_matched, total_notmatched, total_ignored)) in zip(grid, results):
        noss = yes[args.format] if prof.noss else ' '
        ft = yes[args.format] if prof.fixtoken else ' '
        if args.format == 'tex':
            print(' & '.join((args.dataset, prof.strat, noss, ft, str(total_matched), str(total_notmatched), str(total_ignored), str(total_concepts))), ' \\\\ ')
        else:
            print(' | '.join(('', args.dataset, prof.strat, noss, ft, str(total_matched), str(total_notmatched), str(total_ignored), str(total_concepts), '')))


def patch_sids(cli, args):
    rp = TextReport(args.output) if args.output else TextReport()
    if args.gold:
        sents = Document.from_file(args.gold)
        patch_gold_sid(sents)
        rp.write(sents.to_xml_str())
        print("Done")
    else:
        print("No document to patch")


def map_predsense(cli, args):
    ''' Pred-Sense Mapping (gold DMRSes, gold Senses) '''
    rp = TextReport(args.output) if args.output else TextReport()
    rp.header("Pred-Sense mapping / strategy = {}".format(args.strat))
    if args.gold:
        sents = Document.from_file(args.gold)
        if args.patchsid:
            patch_gold_sid(sents)
    else:
        sents = read_gold_mrs()
        patch_gold_sid(sents)
    rp.print("MRS-Sents: {}".format(len(sents)))
    if args.ttl:
        doc = ttl.Document.read_ttl(args.ttl)
    else:
        doc = ttl.Document('gold', path='data').read()
    rp.print("TTL-Sents: {}".format(len(doc)))
    found_sents = 0
    for sent in sents:
        if doc.get(sent.ident) is None:
            cli.logger.warning("Sentence {} could not be found".format(sent.ident))
        else:
            found_sents += 1
    rp.print("Matched: {}".format(found_sents))
    # Now mapping is possible
    # ----------------------------------------
    ct = Counter()  # total
    cm = Counter()  # matched
    cnm = Counter()  # not matched
    cig = Counter()  # ignored
    sense_lemmas = dd(set)  # sense, lemma, map
    sense_sents = dd(set)  # not-matched senses to sentences
    lemma_sents = dd(set)  # not matched lemmas to sentences
    rp.print("Performing Pred-Sense Mapping")
    sents_to_map = sents[:args.topk] if args.topk else sents
    for sent in sents_to_map:
        sent.shallow = doc.get(sent.ident)
        for m, nm, ig in import_shallow(sent, mode=args.strat, no_small_sense=args.noss, fix_token=args.fixtoken, no_nonsense=args.nononsense):
            for c, nid, pred in m:
                ct.count(c.tag)
                cm.count(c.tag)
            for c in ig:
                sense_lemmas[c.tag].add(c.clemma)
                ct.count(c.tag)
                cig.count(c.tag)
            for c in nm:
                sense_lemmas[c.tag].add(c.clemma)
                ct.count(c.tag)
                cnm.count(c.tag)
                sense_sents[c.tag].add(sent)
                lemma_sents[c.clemma].add(sent)
            # print("Sent #{} - Not matched: {}".format(sent.ident, nm))
            # print("           Matched    : {}".format(len(m)))
    rp.header("Not matched", level='h0')
    for sid, c in cnm.most_common():
        rp.print("{}: {} | Lemmas: {}".format(sid, c, sense_lemmas[sid]))
    rp.header("Not matched (by lemma)", level='h0')
    for clemma, sents in sorted(lemma_sents.items(), key=lambda x: len(x[1]), reverse=True):
        rp.print("{}: {} | sents: {}".format(clemma, len(sents), [s.ident for s in sents]))
    if args.matched:
        rp.header("Total", level='h0')
        ct.summarise()
    rp.header("Ignored", level='h0')
    for sid, c in cig.most_common():
        rp.print("{}: {} | Lemmas: {}".format(sid, c, sense_lemmas[sid]))
    # show sense - sentences
    rp.header("Sense - Sentences", level='h0')
    for sid, c in cnm.most_common():
        sents = sense_sents[sid]
        rp.header("{} - {}".format(sid, sense_lemmas[sid]), level='h2')
        for sent in sents:
            ttl_sent = doc.get(sent.ident)
            rp.print(ttl_sent)
            for concept in ttl_sent.concepts:
                if concept.tag == sid:
                    rp.print('  -> {}'.format(concept))
    rp.header("Lemma - Sentences", level='h0')
    for clemma, sents in sorted(lemma_sents.items(), key=lambda x: len(x[1]), reverse=True):
        rp.header("#{}".format(clemma,))
        for sent in sents:
            ttl_sent = doc.get(sent.ident)
            rp.print(ttl_sent)
            for concept in ttl_sent.concepts:
                if concept.clemma == clemma:
                    rp.print('  -> {}'.format(concept))
        rp.print()
    # Show final numbers
    total_concepts = sum(x[1] for x in ct.most_common())
    total_matched = sum(x[1] for x in cm.most_common())
    total_notmatched = sum(x[1] for x in cnm.most_common())
    total_ignored = sum(x[1] for x in cig.most_common())
    rp.header("Summarise")
    rp.print("Total concepts: {}".format(total_concepts))
    rp.print("Matched: {}".format(total_matched))
    rp.print("Not matched: {}".format(total_notmatched))
    rp.print("Ignored: {}".format(total_ignored))
    if args.output:
        print("Total concepts: {}".format(total_concepts))
        print("Matched: {}".format(total_matched))
        print("Not matched: {}".format(total_notmatched))
        print("Ignored: {}".format(total_ignored))
        print("Output file: {}".format(args.output))
    print("Done!")
    return total_concepts, total_matched, total_notmatched, total_ignored


def find_lesk_candidates(cli, args):
    doc = Document.from_file(args.gold)
    ne = 0
    for s in doc:
        if len(s):
            ne += 1
    print("Gold ISF: {} | not empty sents: {}".format(args.gold, ne))
    # candidates = dd(lambda: dd(set))
    notfound = dd(list)
    ident_sent_map = {}
    all_preds = Counter()
    missing_preds = Counter()
    found_preds = Counter()
    with PredSense.wn.ctx() as ctx:
        for idx, sent in enumerate(doc):
            if not len(sent):
                continue
            elif args.ident and sent.ident not in args.ident:
                continue
            if args.topk and args.topk < idx:
                break
            print(sent)
            ident_sent_map[sent.ident] = sent
            dmrs = sent[0].dmrs()
            if dmrs.tags:
                for ep in dmrs.get_lexical_preds():
                    all_preds.count(str(ep.pred))
                    if ep.nodeid in dmrs.tags:
                        # if there is a tag for this node
                        ep_synsets = PredSense.search_ep(ep, ctx=ctx)  # return a SynsetCollection()
                        for tag in dmrs.tags[ep.nodeid]:
                            if tag.synset.ID not in ep_synsets:
                                notfound[sent.ident].append((ep.nodeid, str(ep.pred), tag.synset.ID, tag.synset.lemma, [(x.ID, x.lemma) for x in ep_synsets]))
                                missing_preds.count(str(ep.pred))
                            else:
                                found_preds.count(str(ep.pred))
    output = TextReport(args.output)
    # summarise
    total_found = sum(c for pred, c in found_preds.most_common())
    total_missing = sum(c for pred, c in missing_preds.most_common())
    output.print("Found    : {}".format(total_found))
    output.print("Not found: {}".format(total_missing))
    ratio = (total_missing * 100) / (total_found + total_missing)
    output.print("Missing %: {}".format(ratio))
    # preds by sentences
    output.header("By sentences")
    for sid in sorted(notfound.keys()):
        sent = ident_sent_map[sid]
        output.print((sid, sent.text))
        items = notfound[sid]
        for item in items:
            output.print(item)
        output.print()
    # by preds
    output.header("By preds")
    for pred, occurrence in missing_preds.most_common():
        output.print("{}: {}".format(pred, occurrence))
    print("Done")


def order_preds(cli, args):
    doc = Document.from_file(args.gold)
    output = TextReport(args.output)
    if not args.ident:
        print("No ident was provided")
    for ident in args.ident:
        sent = doc.by_ident(ident, default=None)
        if sent is None:
            print("Sent #{} is missing".format(ident))
        else:
            print(sent)
            eps = sent[0].dmrs().obj().eps()
            sort_eps(eps)
            print(["{}<{}:{}>".format(str(x.pred), x.cfrom, x.cto) for x in eps])
    print("Done")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ISF Gold miner '''
    app = CLIApp(desc='ISF Gold mining Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('fix', func=fix_gold)
    task.add_argument('-o', '--output', help='Output file', default=None)

    task = app.add_task('mapbm', func=map_all)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-t', '--ttl', help='TTL profile', default=None)
    task.add_argument('-n', '--topk', help='Only process top k sentences', type=int)
    task.add_argument('-p', '--prefix', help='Output ', default='data/mapbm')
    task.add_argument('-d', '--dataset', help='Dataset name', default='DMRS')
    task.add_argument('-f', '--format', help='Output format', choices=['org', 'tex'], default='org')

    task = app.add_task('map', func=map_predsense)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-t', '--ttl', help='TTL profile', default=None)
    task.add_argument('-o', '--output', help='Output file', default=None)
    task.add_argument('-s', '--strat', help='Strategy', choices=[Lexsem.NAIVE, Lexsem.STRICT, Lexsem.ROBUST], default=Lexsem.NAIVE)
    task.add_argument('-n', '--topk', help='Only process top k sentences', type=int)
    task.add_argument('-M', '--matched', help='Show matched', action='store_true')
    task.add_argument('--noss', help='No small sense', action='store_true')
    task.add_argument('--fixtoken', help='Auto fix token', action='store_true')
    task.add_argument('--nononsense', help='Auto fix token', action='store_true')
    task.add_argument('--patchsid', help='Force patching sentence ID', action='store_true')

    task = app.add_task('patch', func=patch_sids)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-o', '--output', help='Output file', default=None)

    task = app.add_task('order', func=order_preds)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-o', '--output', help='Output file', default=None)
    task.add_argument('--ident', nargs='*')

    task = app.add_task('leskcan', func=find_lesk_candidates)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-o', '--output', help='Output file', default=None)
    task.add_argument('-n', '--topk', help='Only process top k sentences', type=int)
    task.add_argument('--ident', nargs='*')
    # run app
    app.run()


if __name__ == "__main__":
    main()
