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
from chirptext import chio

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

def patch_gold_sid(sents, seed=10000):
    ''' patch TSDB ident to NTU format '''
    for idx, s in enumerate(sents):
        s.ident = idx + seed


def read_ttl(ttl_path, ttl_format=ttl.MODE_TSV):
    return ttl.read(ttl_path, ttl_format)


def fix_gold(cli, args):
    ''' Generate SQLite script to patch typo in IMI's data '''
    sents = read_gold_mrs()
    patch_gold_sid(sents)
    print("Gold sentences: {}".format(len(sents)))
    doc = read_ttl(args.input, ttl_format=args.ttl_format)
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
    ''' Batch mapping '''
    grid = [
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, ttl_format=args.ttl_format, output="{}_naive.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, fixtoken=True, ttl_format=args.ttl_format, output="{}_naive_ft.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, noss=True, ttl_format=args.ttl_format, output="{}_naive_noss.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.NAIVE, noss=True, fixtoken=True, ttl_format=args.ttl_format, output="{}_naive_noss_ft.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.ROBUST, noss=True, fixtoken=True, ttl_format=args.ttl_format, output="{}_robust.txt".format(args.prefix)),
        DO(ttl=args.ttl, gold=args.gold, topk=args.topk, strat=Lexsem.STRICT, noss=True, fixtoken=True, ttl_format=args.ttl_format, output="{}_strict.txt".format(args.prefix)),
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
    # rp = TextReport(args.output) if args.output else TextReport()
    if args.gold:
        print("Gold MRS file: {}".format(args.gold))
        sent_ids = []
        if args.idfile:
            print("ID file: {}".format(args.idfile))
            idlines = chio.read_file(args.idfile).splitlines()
            for line in idlines:
                idx, text = line.split('\t', maxsplit=1)
                sent_ids.append((idx, text))
            print("Found {} sentences in ID file".format(len(sent_ids)))
        sents = Document.from_file(args.gold)
        if sent_ids:
            if len(sent_ids) != len(sents):
                print("Wrong sent ID files - Found ID: {} | Found MRS: {}".format(len(sent_ids), len(sents)))
            print("Verifying sentences' text")
            for ((sid, stext), mrs_sent) in zip(sent_ids, sents):
                if stext and stext != mrs_sent.text:
                    print("Invalid sentence text: sentID: {} | {} <> {}".format(sid, stext, mrs_sent.text))
                    exit()
            print("Sentences are verified, proceed to patch sent idents")
            for ((sid, stext), mrs_sent) in zip(sent_ids, sents):
                mrs_sent.ident = sid
                if args.both:
                    mrs_sent.ID = sid
        else:
            patch_gold_sid(sents)

        if args.output:
            print("Sentence idents are patched, writing to output XML file to: {}...".format(args.output))
            chio.write_file(args.output, sents.to_xml_str())
        else:
            print(sents.to_xml_str())
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
    # ignore empty sentence
    empty_sents = [s for s in sents if not len(s)]
    not_empty_sents = [s for s in sents if len(s)]
    rp.print("MRS-Sents: {}".format(len(sents)))
    rp.print("MRS-Sents not empty: {}".format(len(not_empty_sents)))
    if args.ttl:
        doc = ttl.read(args.ttl, mode=args.ttl_format)
    else:
        # [XXX] using gold by default is bad ...
        doc = ttl.Document(name='gold', path='data').read()
    rp.print("TTL-Sents: {}".format(len(doc)))
    found_sents = 0
    for sent in not_empty_sents:
        if doc.get(sent.ident) is None:
            cli.logger.warning("Sentence {} could not be found".format(sent.ident))
        else:
            found_sents += 1
    rp.print("Matched: {}".format(found_sents))
    rp.print("Empty sentences: {}".format([s.ident for s in empty_sents]))
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
    sents_to_map = not_empty_sents[:args.topk] if args.topk else not_empty_sents
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


def isf_to_ukb(cli, args):
    ''' ISF to UKB '''
    doc = Document.from_file(args.input)
    output = TextReport(args.output)
    tokenfile = TextReport(args.output + '.tokens.txt')
    report = TextReport(args.report)
    report.print("Output file: {}".format(args.output))
    processed = 0
    if not args.ident:
        report.print("No ident was provided")
    for idx, sent in enumerate(doc):
        # sent = doc.by_ident(ident, default=None)
        if args.topk and idx > args.topk:
            break
        if args.ident and sent.ident not in args.ident:
            continue
        if sent is None:
            report.print("Sent #{} is missing".format(sent.ident))
        elif len(sent) == 0:
            report.print("Sent #{} is empty (i.e. there is no parse)".format(sent.ident))
        else:
            sentid = sent.ID if sent.ID else sent.ident
            report.print("Processing {}".format(sentid))
            tokens = sent.readings[0].dmrs().tokenize_pos(strict=args.strict)
            if not tokens:
                report.print("Empty DMRS: {} (no pred???)".format(sentid))
                continue
            # sentense is OK ...
            output.print(sentid)
            for idx, (isf_lemma, pos, cfrom, cto) in enumerate(tokens):
                # In UKB's lemmas, use _ to represent a space
                lemma = isf_lemma.replace('+', '_')
                output.write("{text}#{p}#w{wid}#1 ".format(text=lemma, p=pos, wid=idx))
                tokenfile.writeline('\t'.join((str(sentid), str(idx), str(cfrom), str(cto))))
            output.write('\n\n')
            processed += 1
    report.print("Processed {} sentence(s)".format(processed))
    report.print("Done")


def order_preds(cli, args):
    doc = Document.from_file(args.gold)
    output = TextReport(args.output)
    if not args.ident:
        output.print("No ident was provided")
    for ident in args.ident:
        sent = doc.by_ident(ident, default=None)
        if sent is None:
            output.print("Sent #{} is missing".format(ident))
        else:
            output.print(sent)
            eps = sent[0].dmrs().obj().eps()
            sort_eps(eps)
            output.print(["{}<{}:{}>".format(str(x.pred), x.cfrom, x.cto) for x in eps])
    output.print("Done")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ISF Gold miner '''
    app = CLIApp(desc='ISF Gold mining Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('fix', func=fix_gold)
    task.add_argument('input', help='Path to TTL file')
    task.add_argument('-o', '--output', help='Output file', default=None)
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_JSON, choices=[ttl.MODE_JSON, ttl.MODE_TSV])
    # task.add_argument('--seed', default=1, type=int)


    task = app.add_task('mapbm', func=map_all)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-t', '--ttl', help='TTL profile', default=None)
    task.add_argument('-n', '--topk', help='Only process top k sentences', type=int)
    task.add_argument('-p', '--prefix', help='Output ', default='data/mapbm')
    task.add_argument('-d', '--dataset', help='Dataset name', default='DMRS')
    task.add_argument('-f', '--format', help='Output format', choices=['org', 'tex'], default='org')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('map', func=map_predsense)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-t', '--ttl', help='TTL profile', default=None)
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])
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
    task.add_argument('--idfile', help='ID file in TSV format, 1st column is ID, 2nd column is text (optional)')
    task.add_argument('--both', help='Patch both sentences IDs and idents', action='store_true')
    task.add_argument('-o', '--output', help='Output file', default=None)

    task = app.add_task('order', func=order_preds)
    task.add_argument('-g', '--gold', help='Gold MRS', default=None)
    task.add_argument('-o', '--output', help='Output file', default=None)
    task.add_argument('--ident', nargs='*')

    task = app.add_task('to_ukb', func=isf_to_ukb)
    task.add_argument('input', help='MRS XML file')
    task.add_argument('output', help='Output file')
    task.add_argument('--strict', help='Strict mode, use this flag to ignore all grammar predicates without CARGs', action='store_true')
    task.add_argument('--report', help='Report file', default=None)
    task.add_argument('-n', '--topk', help='Only process top k sentences', type=int)
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
