#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Script for processing TTL profiles

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

import os
import logging
import json
from collections import defaultdict as dd

from lelesk.util import ptpos_to_wn
from chirptext import TextReport, Counter, piter
from chirptext.cli import CLIApp, setup_logging
from chirptext import chio
from chirptext.chio import CSV
from chirptext import texttaglib as ttl
from yawlib import SynsetID
from yawlib.helpers import get_omw, get_wn

from coolisf.common import read_file, overlap


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


NONSENSES = ['02604760-v',  # : 85 | have the quality of being - ['be']
             '00024073-r',  #: 22 | negation of a word or group of words - ['not', 'non', "n't"]
             '02749904-v',  #: 15 | happen, occur, take place - ['be']
             '01552885-a',  #: 9 | a quantifier that can be used with count nouns and is often preceded by `a'; a small but indefinite number - ['few']
             '02655135-v',  #: 8 | occupy a certain position or area; be somewhere - ['be']
             '01712704-v',  #: 5 | carry out or perform an action - ['do', 'execute', 'perform']
             '02603699-v',  #: 5 | have an existence, be extant - ['be', 'exist']
             '00031899-r',  #: 5 | used to give emphasis - ['very', 'really', 'real', 'rattling']
             '02560585-v',  #: 4 | engage in - ['do', 'make']
             ]


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def read_ttl(ttl_path, ttl_format=ttl.MODE_TSV):
    return ttl.read(ttl_path, ttl_format)


def get_ttl_writer(path, ttl_format=ttl.MODE_TSV, id_seed=1):
    if ttl_format == ttl.MODE_JSON:
        return ttl.JSONWriter.from_path(path, id_seed=id_seed)
    else:
        return ttl.TxtWriter.from_path(path, id_seed=id_seed)


def prepare_tags(doc, args=None, nonsense=True):
    ''' Return a map of sentID -> map of {synsetid:(cfrom:cto)}, number of used tags (int), and ignored tags (int)'''
    tags = dd(lambda: dd(set))
    tagcount = 0
    ignored = 0
    for s in doc:
        for tag in s.tags:
            cfrom = int(tag.cfrom)
            cto = int(tag.cto)
            if tag.tagtype in ('WN', 'EXTRA', 'OMW'):
                # ignore nonsense
                if not nonsense and tag.label in NONSENSES:
                    ignored += 1
                    continue
                tags[s.ID][tag.label].add((cfrom, cto))
                tagcount += 1
            else:
                ignored += 1
                if args and not args.quiet:
                    getLogger().warning("Unknown label: {} in sentence #{}".format(tag.tagtype, s.ID))
    return tags, tagcount, ignored


def score(gold_tags, profile_tags, args=None):
    matched = set()
    notmatched = set()  # false negative
    for sid in gold_tags.keys():
        gstags = gold_tags[sid]  # gold tags of this sent
        pstags = profile_tags[sid]  # profile tags of this sent
        for gstag in gstags.keys():  # gstag = synsetID
            glocs = gstags[gstag]
            plocs = set(pstags[gstag]) if gstag in pstags else []
            for gfrom, gto in glocs:
                tag = (sid, gfrom, gto, gstag)  # sentID, gfrom, gto, synsetID
                for pfrom, pto in plocs:
                    getLogger().debug("Checking {}:{} againts {}:{}".format(gfrom, gto, pfrom, pto))
                    if overlap(pfrom, pto, gfrom, gto):
                        matched.add(tag)
                        plocs.remove((pfrom, pto))
                        break
                if tag not in matched:
                    if args and not args.quiet:
                        getLogger().warning("Not found: {}".format(tag))
                    notmatched.add(tag)
    return matched, notmatched
    # return gold_tags.intersection(profile_tags)


def compare_ttls(cli, args):
    ''' Compare TTL to gold '''
    rp = TextReport()
    omw = get_omw()
    ctx = omw.ctx()
    gold = None
    profile = None
    ignored_ids = []
    if args.ignore:
        ignored_ids = [x.strip() for x in read_file(args.ignore).splitlines()]
        getLogger().debug("Ignored sentence IDs: {}".format(', '.join(ignored_ids)))
    if args.gold_profile:
        gold = read_ttl(args.gold_profile, ttl_format=args.ttl_format)
        # remove ignored sentences
        if ignored_ids:
            for sid in ignored_ids:
                gold.pop(sid, default=None)
        if not args.batch:
            rp.header("Gold sentences: {} | Loc: {}".format(len(gold), args.gold_profile))
        if args.verbose and not args.batch:
            for s in gold:
                rp.print("Sent #{}: {} tags".format(s.ID, len(s.tags)))
    elif not args.batch:
        print("Oops, no gold!")
    # read profile
    if args.profile:
        profile = read_ttl(args.profile, ttl_format=args.ttl_format)
        rp.header("Profile sentences: {} | Loc: {}".format(len(profile), args.profile))
        # remove ignored sentences
        if ignored_ids:
            for sid in ignored_ids:
                profile.pop(sid, default=None)
        if not args.batch:
            rp.header("Profile sentences: {} (ignored: {}) | Loc: {}".format(len(profile), len(ignored_ids), args.profile))
        if args.verbose and not args.batch:
            for s in profile:
                getLogger().debug("Profile/Sent #{}: {} tags".format(s.ID, len(s.tags)))
    elif not args.batch:
        print("Oops, no profile to evaluate")
    # calculate precision and recall
    if gold and profile:
        gold_tags, gold_tags_len, gold_ignored = prepare_tags(gold, args=args, nonsense=args.nonsense)
        profile_tags, profile_tags_len, profile_ignored = prepare_tags(profile, args=args, nonsense=args.nonsense)
        if gold_tags_len == 0:
            rp.print("WARNING: There was no tag found in the gold profile. Please make sure that the tags for comparison are *sentence level* tags")
        if profile_tags_len == 0:
            rp.print("WARNING: There was no tag found in the evaluating profile. Please make sure that the tags for comparison are *sentence level* tags")
        getLogger().debug("Gold tags: {}".format(gold_tags_len))
        getLogger().debug(list(gold_tags.items())[:5])
        getLogger().debug("Profile tags: {}".format(profile_tags_len))
        getLogger().debug(list(profile_tags.items())[:5])
        true_positive, false_negative = score(gold_tags, profile_tags, args=args)
        precision = len(true_positive) / profile_tags_len
        recall = len(true_positive) / gold_tags_len
        f1 = 2 * precision * recall / (precision + recall)
        getLogger().debug("TP: {}".format(len(true_positive)))
        getLogger().debug("FN: {}".format(len(false_negative)))
        getLogger().debug("Recall (TP/Gtags): {}".format(recall))
        getLogger().debug("Precision (TP/Ptags): {}".format(precision))
        getLogger().debug("F1 (2*p*r/(p+r)): {}".format(f1))
        rc_text = "{:.2f}%".format(recall * 100)
        pr_text = "{:.2f}%".format(precision * 100)
        f1_text = "{:.2f}%".format(f1 * 100)
        if not args.batch:
            rp.print("True positive: {}".format(len(true_positive)))
            rp.print("False Negative: {}".format(len(false_negative)))
            rp.print("Gold # senses: {} | Ignored: {} | Total: {}".format(gold_tags_len, gold_ignored, gold_tags_len + gold_ignored))
            rp.print("Predicted # senses: {} | Ignored: {} | Total: {}".format(profile_tags_len, profile_ignored, profile_tags_len + profile_ignored))
            rp.print("Recall:    {}".format(rc_text))
            rp.print("Precision: {}".format(pr_text))
            rp.print("F1       : {}".format(f1_text))
        if args.org:
            # output org-mode
            columns = [rc_text, pr_text, f1_text]
            if args.cols:
                columns = args.cols + columns
            rp.print('| {} |'.format(' | '.join(columns)))
        if args.debug:
            if not args.batch:
                print("Debug file: {}".format(args.debug))
            debugfile = TextReport(args.debug)
            debugfile.print(".:: Table of content ::.")
            debugfile.print("")
            debugfile.print("[Misisng senses]")
            debugfile.print("[By classes]")
            debugfile.print("[Summary]")
            debugfile.print("")
            ss_map = {}
            debugfile.header("[Missing senses]")
            for sid, cfrom, cto, label in sorted(false_negative):
                if label not in ss_map:
                    ss = omw.get_synset(label, ctx=ctx)
                    ss_map[label] = ss
                else:
                    ss = ss_map[label]
                # get the surface form
                surface = gold.get(sid).text[int(cfrom):int(cto)]
                debugfile.print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(sid, cfrom, cto, surface, label, ss.definition, ss.lemmas))
            # by classes
            c = Counter()
            c.update(synsetID for sentID, cfrom, cto, synsetID in false_negative)
            debugfile.header("[By classes]")
            for synsetID, freq in c.most_common():
                ss = ss_map[synsetID]
                debugfile.print("{}: {} | ({}) - {}".format(synsetID, freq, ', '.join(ss.lemmas), ss.definition))
            # summary
            debugfile.header("[Summary]")
            debugfile.print("True positive: {}".format(len(true_positive)))
            debugfile.print("False positive: {}".format(len(false_negative)))
            debugfile.print("Gold # senses: {} | Ignored: {} | Total: {}".format(gold_tags_len, gold_ignored, gold_tags_len + gold_ignored))
            debugfile.print("Predicted # senses: {} | Ignored: {} | Total: {}".format(profile_tags_len, profile_ignored, profile_tags_len + profile_ignored))
            debugfile.print("Recall (TP/Gtags)   : {}".format(rc_text))
            debugfile.print("Precision (TP/Ptags): {}".format(pr_text))
            debugfile.print("F1  (2*p*r/(p+r))   : {}".format(f1_text))
    ctx.close()


def pop_concept(sent, c):
    if c not in sent.concepts:
        return
    getLogger().debug("Popping concept {} from sent #{}".format(c, sent.ID))
    cfrom = min(t.cfrom for t in c.tokens)
    cto = min(t.cto for t in c.tokens)
    synset = c.tag
    sent.pop_concept(c.cidx)
    remove_tags = set()
    # remove tags in sentence as well
    for tag in sent.tags:
        if (int(tag.cfrom), int(tag.cto), tag.label) == (cfrom, cto, synset):
            remove_tags.add(tag)
    if remove_tags:
        for tag in remove_tags:
            getLogger().debug("Removing tag: {}".format(tag))
            sent.tags.remove(tag)
    return remove_tags


def remove_msw_ttl(cli, args):
    doc = read_ttl(args.path)
    rp = TextReport(args.debug)
    rp.print("Doc size: {}".format(len(doc)))
    orig_tag_count = 0
    orig_concept_count = 0
    for s in doc:
        orig_concept_count += len(s.concepts)
        orig_tag_count += len(s.tags)
    print("# tags: {}".format(orig_tag_count))
    print("# concepts: {}".format(orig_concept_count))
    manual = dd(lambda: dd(dict))
    if args.manual:
        entries = CSV.read_tsv(args.manual)
        for sid, wid, tag, keep, lemma in entries:
            sid, wid = int(sid), int(wid)
            if not lemma:
                manual[sid][wid][tag] = int(keep)
            else:
                manual[sid][wid][(tag, lemma)] = int(keep)
    wn = get_wn()
    ctx = wn.ctx()
    nope_synsets = set()
    ok_synsets = set()
    if args.wn30:
        rp.print("WN30 filter is activated")
    for sidx, sent in enumerate(doc):
        if args.topk and sidx > int(args.topk):
            break
        getLogger().debug("Processing sentence {}/{}".format(sidx + 1, len(doc)))
        getLogger().debug("Before concepts: {}".format(sent.concepts))
        getLogger().debug("Before tags: {}".format(sent.tags))
        # remove concepts that are not in PWN 3.0
        if args.wn30:
            remove_tags = set()
            for tag in sent.tags:
                if tag.tagtype == 'OMW':
                    remove_tags.add(tag)
            for tag in remove_tags:
                sent.tags.remove(tag)
            remove_concepts = set()
            for c in sent.concepts:
                if c.tag in ok_synsets:
                    pass
                elif c.tag in nope_synsets:
                    remove_concepts.add(c)
                    # pop_concept(sent, c)
                elif wn.get_synset(c.tag, ctx=ctx) is None:
                    # remove it
                    nope_synsets.add(c.tag)
                    remove_concepts.add(c)
                    # pop_concept(sent, c)
                else:
                    ok_synsets.add(c.tag)
            for c in remove_concepts:
                pop_concept(sent, c)
        msw = list(sent.msw())
        tcmap = sent.tcmap()
        # remove_tags = set()
        if msw:
            keep_remove = []
            for w in msw:
                max_len = 0
                keep = []
                remove = set()
                wid = sent.tokens.index(w)
                for c in tcmap[w]:
                    if c.tag in manual[sent.ID][wid]:
                        if manual[sent.ID][wid][c.tag]:
                            keep.append(c)
                        else:
                            remove.add(c)
                    elif (c.tag, c.clemma) in manual[sent.ID][wid]:
                        if manual[sent.ID][wid][(c.tag, c.clemma)]:
                            keep.append(c)
                        else:
                            remove.add(c)
                    elif len(c.tokens) == 1 or len(c.tokens) < max_len:
                        remove.add(c)
                    else:
                        max_len = len(c.tokens)
                        keep.append(c)
                if len(keep) != 1:
                    keep_remove.append((w, keep, remove))
                else:
                    # everything is OK, remove them now
                    for c in remove:
                        if args.debug:
                            rp.print("Removing concept {} from {}".format(c, sent.ID))
                        getLogger().debug("Removing concept {} from {}".format(c, sent.ID))
                        pop_concept(sent, c)
            if keep_remove:
                rp.header(sent)
                for w, keep, remove in keep_remove:
                    rp.write(w)
                    rp.writeline(" - Keep: {} | Remove: {}".format(keep, remove))
        # remove sent's tags
        # for tag in remove_tags:
        #     getLogger().debug("removing tag: {}".format(tag))
        #     sent.tags.remove(tag)
        getLogger().debug("After concepts: {}".format(sent.concepts))
        getLogger().debug("After tags: {}".format(sent.tags))
    if nope_synsets:
        rp.print("Noped synsets: {}".format(nope_synsets))
    if args.output:
        doc_path = os.path.dirname(args.output)
        doc_name = os.path.basename(args.output)
        new_doc = ttl.Document(doc_name, doc_path)
        sents = doc if not args.topk else list(doc)[:int(args.topk)]
        for s in sents:
            new_doc.add_sent(s)
        tag_count = 0
        concept_count = 0
        for s in sents:
            concept_count += len(s.concepts)
            tag_count += len(s.tags)
        print("[New] # tags: {}".format(tag_count))
        print("[New] # concepts: {}".format(concept_count))
        rp.print("Writing fixed TTL to {}".format(new_doc.sent_path))
        new_doc.write_ttl()


def strip_ttl(cli, args):
    doc = read_ttl(args.path)
    print("In doc: {} | Sentences: {}".format(args.path, len(doc)))
    if args.noconcept:
        for sent in doc:
            cids = [c.cidx for c in sent.concepts]
            for cid in cids:
                sent.pop_concept(cid)
    if args.notag:
        for sent in doc:
            sent.tags.clear()
    if args.output:
        print("Writing output to: {}".format(args.output))
        doc_path = os.path.dirname(args.output)
        doc_name = os.path.basename(args.output)
        new_doc = ttl.Document(doc_name, doc_path)
        for s in doc:
            new_doc.add_sent(s)
        new_doc.write_ttl()
    print("Done")


def bake_doc(doc):
    ''' Convert concepts to tags '''
    for sent in doc:
        for concept in sent.concepts:
            cfrom = min(t.cfrom for t in concept.tokens)
            cto = min(t.cto for t in concept.tokens)
            sid = SynsetID.from_string(concept.tag, default=None)  # must be a valid synsetID
            if cfrom >= 0 and cto >= 0 and sid is not None:
                sent.new_tag(concept.tag, cfrom, cto, tagtype='WN')
    return doc


def concept_to_tags(cli, args):
    doc = read_ttl(args.path, ttl_format=args.ttl_format)
    print("In doc: {} | Sentences: {}".format(args.path, len(doc)))
    bake_doc(doc)
    if args.output:
        ttl.write(args.output, doc, mode=args.ttl_format)
    print("Done")


def ttl_to_txt(cli, args):
    doc = read_ttl(args.path)
    print("In doc: {} | Sentences: {}".format(args.path, len(doc)))
    lines = [s.text for s in doc]
    if args.output:
        chio.write_file(args.output, '\n'.join(lines))
        print("Written {} lines to {}".format(len(lines), args.output))
    print("Done")


def ttl_to_ukb(cli, args):
    ''' Convert TTL file to UKB file '''
    doc = read_ttl(args.input, ttl_format=args.ttl_format)
    print("In doc: {} | Sentences: {}".format(args.input, len(doc)))
    if args.output:
        with chio.open(args.output, mode='wt') as outfile:
            for sent in doc:
                outfile.write('{}\n'.format(sent.ID))
                for idx, w in enumerate(sent):
                    outfile.write("{text}#{p}#w{wid}#1 ".format(text=w.text.lower(), p=ptpos_to_wn(w.pos), wid=idx))
                outfile.write('\n\n')
        print("[TTL => UKB] Written {} lines to {}".format(len(doc), args.output))
    print("Done")


def ukb_to_ttl(cli, args):
    ''' Convert UKB output to TTL '''
    doc = read_ttl(args.ttl, ttl_format=args.ttl_format)
    print("Source TTL file: {} | Sentences: {}".format(args.ttl, len(doc)))
    c = Counter()
    sids = set()
    input_sids = {int(s.ID) for s in doc}
    for line_idx, line in enumerate(chio.read_file(args.input).splitlines()):
        if line.startswith('!! '):
            continue
        parts = line.split()
        if len(parts) != 5:
            print("WARNING: Invalid line -> {}: {}".format(line_idx, line))
            continue
        sid_text, wid_text, synsetid, unknown, lemma = line.split()
        sid = int(sid_text)
        wid = int(wid_text[1:])
        sent_obj = doc.get(sid, default=None)
        if sent_obj is None:
            print("SID #{} could not be found".format(sid))
        elif wid >= len(sent_obj):
            print("Invalid wid: line#{} - sent#{} - wid#{}".format(line_idx, sid, wid))
        else:
            token = sent_obj[wid]
            if lemma != token.text.lower():
                print("Invalid token text: {} <> {}".format(lemma, token.text.lower()))
            # now can tag ...
            sent_obj.new_concept(synsetid, lemma, tokens=[wid])
            c.count("Tokens")
            sids.add(sid)
            # print(sent_obj)
            # print("sid:{} - wid:{} - {} ({}) => token:{}".format(sid, wid, synsetid, lemma, sent_obj[wid].text))        
    print("SRC sentences: {}".format(len(input_sids)))
    print("UKB sentences: {}".format(len(sids)))
    print("Not found: {}".format(input_sids.difference(sids)))
    c.summarise()
    print("Now baking to tags ...")
    bake_doc(doc)
    # Now output ...
    if args.output:
        print("Output to file ...")
        _writer = get_ttl_writer(args.output, ttl_format=args.ttl_format, id_seed=args.seed)
        for sent in doc:
            _writer.write_sent(sent)
        print("Written {} sentences to {}".format(len(doc), args.output))
    print("Done")


def tsv_to_json(cli, args):
    doc_tsv = read_ttl(args.input)
    _json_writer = ttl.JSONWriter.from_path(args.output)
    for sent in doc_tsv:
        if args.textonly:
            _json_writer.write_sent(ttl.Sentence(sent.text))
        else:
            _json_writer.write_sent(sent)
    print("Create JSON file: {}".format(args.output))


def fix_ttl_id(cli, args):
    ''' Fix sentence ID '''
    in_doc = read_ttl(args.input, ttl_format=args.ttl_format)
    out_doc = get_ttl_writer(args.output, ttl_format=args.ttl_format)
    for idx, sent in enumerate(in_doc):
        sent.ID = args.seed + idx
        out_doc.write_sent(sent)
    print("Fixed file: {}".format(args.output))


def txt_to_ttl(cli, args):
    print("Input file: {}".format(args.input))
    print("TTL/{} output: {}".format(args.ttl_format, args.output))
    print("With ID column: {}".format(args.with_idcolumn))
    raw_sents = chio.read_file(args.input).splitlines()
    _writer = get_ttl_writer(args.output, ttl_format=args.ttl_format, id_seed=args.seed)
    for sent in raw_sents:
        if args.with_idcolumn:
            sid, text = sent.split('\t', maxsplit=1)
            _writer.write_sent(ttl.Sentence(text=text, ID=sid))
        else:
            _writer.write_sent(ttl.Sentence(text=text))
    print("Written {} sentences to {}".format(len(raw_sents), args.output))


def import_ttl_data(cli, args):
    doc = read_ttl(args.path)
    print("In doc: {} | Sentences: {}".format(args.path, len(doc)))
    # import tokens
    if args.tokens:
        p = piter(chio.read_tsv_iter(args.tokens))
        groups = []
        current = []
        for row in p:
            if row:
                current.append(row)
            if not p.peep() or not p.peep().value:
                if current:
                    groups.append(current)
                    current = []
        print("Found {} sentences.".format(len(groups)))
        if len(groups) != len(doc):
            print("Wrong token files")
            exit()
        for sent, row in zip(doc, groups):
            sent.tokens = [tk[0] for tk in row]
            for token, (text, pos) in zip(sent, row):
                token.text = text
                token.pos = pos
    # output stuff
    if args.output:
        ttl.TxtWriter.from_path(args.output).write_doc(doc)
        print("Written {} sentences to {}".format(len(doc), args.output))
    print("Done")


def corenlp_to_ttl(cli, args):
    print("Core NLP output file: {}".format(args.input))
    print("TTL file: {}".format(args.output))
    print("Source (raw) file: {}".format(args.raw))
    cn_sents = json.loads(chio.read_file(args.input))['sentences']
    print("Found {} core-nlp sents".format(len(cn_sents)))
    raw_sents = chio.read_file(args.raw).splitlines()
    _writer = get_ttl_writer(args.output, ttl_format=args.ttl_format, id_seed=args.seed)
    for sent_text, cn_sent in zip(raw_sents, cn_sents):
        ttl_sent = ttl.Sentence(sent_text)
        ttl_sent.tokens = (cn_tk['originalText'] for cn_tk in cn_sent['tokens'])
        for ttl_tk, cn_tk in zip(ttl_sent, cn_sent['tokens']):
            if 'lemma' in cn_tk:
                ttl_tk.lemma = cn_tk['lemma']
            if 'pos' in cn_tk:
                ttl_tk.pos = cn_tk['pos']
        _writer.write_sent(ttl_sent)
    print("{} sentences was written to {}".format(len(raw_sents), args.output))


def semeval_to_ttl(cli, args):
    print("Semeval file: {}".format(args.input))
    print("TTL file: {}".format(args.output))
    print("TTL format: {}".format(args.ttl_format))


def check_ttl_stats(cli, args):
    gold = read_ttl(args.path, ttl_format=args.ttl_format)
    tag_count = 0
    for sent in gold:
        tag_count += len([t for t in sent.tags if t.tagtype in ('WN', 'EXTRA', 'OMW')])
    print("Sense count: {}".format(tag_count))


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' TTL processors '''
    app = CLIApp(desc='ISF TTL Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('cmp', func=compare_ttls)
    task.add_argument('-g', '--gold_profile', help='Gold Profile', default=None)
    task.add_argument('-p', '--profile', help='Profile for evaluation', default=None)
    task.add_argument('--debug', help='Debug file')
    task.add_argument('--ignore', help='Sentence IDs to ignore')
    task.add_argument('--nonsense', help='Count nonsense tags too', action="store_true")
    task.add_argument('--batch', help='Output in batch mode only (no detailed summary)', action="store_true")
    task.add_argument('--org', help='Output ORG-mode format', action="store_true")
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])
    task.add_argument('--cols', help='Extra columns', nargs='*')
    task.add_argument('--bake', action='store_true')

    task = app.add_task('msw', func=remove_msw_ttl)
    task.add_argument('path', help='Path to TTL document')
    task.add_argument('--manual', help='Manual entries to be removed')
    task.add_argument('--wn30', help='Only keep PWN3.0 synsets', action='store_true')
    task.add_argument('-n', '--topk', help='Only process top k items')
    task.add_argument('-o', '--output', help='New TTL path')
    task.add_argument('--debug', help='Debug file')

    task = app.add_task('strip', func=strip_ttl)
    task.add_argument('path', help='Path to TTL document')
    task.add_argument('--noconcept', help='Remove concepts', action='store_true')
    task.add_argument('--notag', help='Remove tags', action='store_true')
    task.add_argument('-o', '--output', help='New TTL path')

    task = app.add_task('bake', func=concept_to_tags)
    task.add_argument('path', help='Path to TTL document')
    task.add_argument('-o', '--output', help='New TTL path')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('stats', func=check_ttl_stats)
    task.add_argument('path', help='Path to TTL document')
    task.add_argument('-o', '--output', help='Output log file')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('totxt', func=ttl_to_txt)
    task.add_argument('path', help='Path to TTL document')
    task.add_argument('-o', '--output', help='Output text file')

    task = app.add_task('tojson', func=tsv_to_json)
    task.add_argument('input', help='Path to TTL/TSV document')
    task.add_argument('output', help='Path to TTL/JSON output document')
    task.add_argument('--textonly', action='store_true')

    task = app.add_task('fixid', func=fix_ttl_id)
    task.add_argument('input', help='Path to TTL/TSV document')
    task.add_argument('output', help='Path to TTL/JSON output document')
    task.add_argument('--seed', default=10000, type=int)
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('fromtxt', func=txt_to_ttl)
    task.add_argument('input', help='Path to TXT file')
    task.add_argument('output', help='Path to TTL output document')
    task.add_argument('--seed', default=10000, type=int)
    task.add_argument('--with_idcolumn', action='store_true')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_JSON, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('import', func=import_ttl_data)
    task.add_argument('path', help='Path to TTL document')
    task.add_argument('-o', '--output', help='Output text file')
    task.add_argument('--tokens', help='Path to token file')

    task = app.add_task('corenlp', func=corenlp_to_ttl)
    task.add_argument('input', help='Path to core NLP file')
    task.add_argument('output', help='Path to TTL/JSON output document')
    task.add_argument('--raw', help='Raw file')
    task.add_argument('--seed', default=1, type=int)
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('semeval', func=semeval_to_ttl)
    task.add_argument('input', help='Path to semeval file')
    task.add_argument('output', help='Path to TTL/JSON output document')
    task.add_argument('--raw', help='Raw file')
    task.add_argument('--seed', default=1, type=int)
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_JSON, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('to_ukb', func=ttl_to_ukb)
    task.add_argument('input', help='Path to TTL file')
    task.add_argument('output', help='Path to UKB output file')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_JSON, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    task = app.add_task('ukb', func=ukb_to_ttl)
    task.add_argument('input', help='Path to UKB output file')
    task.add_argument('ttl', help='Input TTL file')
    task.add_argument('-o', '--output', help='Path to TTL output file')
    task.add_argument('--seed', default=1, type=int)
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_JSON, choices=[ttl.MODE_JSON, ttl.MODE_TSV])


    # run app
    app.run()


if __name__ == "__main__":
    main()
