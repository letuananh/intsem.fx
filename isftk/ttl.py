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

from chirptext import TextReport
from chirptext.cli import CLIApp, setup_logging
from chirptext import texttaglib as ttl


# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# Functions
# ------------------------------------------------------------------------------

def read_ttl(ttl_path):
    ttl.Document.read_ttl(ttl_path)


def prepare_tags(doc):
    tags = set()
    for s in doc:
        for tag in s.tags:
            if tag.tagtype == 'WN':
                tags.add((s.ID, tag.cfrom, tag.cto, tag.label))
            else:
                getLogger().warning("Unknown label: {} in sentence #{}".format(tag.tagtype, s.ID))
    return tags


def compare_ttls(cli, args):
    ''' Compare TTL to gold '''
    rp = TextReport()
    gold = None
    profile = None
    if args.gold_profile:
        gold = read_ttl(args.gold_profile)
        rp.header("Gold sentences: {}".format(len(gold)))
        for s in gold:
            rp.print("Sent #{}: {} tags".format(s.ID, len(s.tags)))
    else:
        print("Oops, no gold!")
    # read profile
    if args.profile:
        profile = read_ttl(args.profile)
        rp.header("Profile sentences: {}".format(len(profile)))
        for s in profile:
            rp.print("Sent #{}: {} tags".format(s.ID, len(s.tags)))
    else:
        print("Oops, no profile to evaluate")
    # calculate precision and recall
    if gold and profile:
        gold_tags = prepare_tags(gold)
        profile_tags = prepare_tags(profile)
        true_positive = gold_tags.intersection(profile_tags)
        precision = len(true_positive) / len(profile_tags)
        recall = len(true_positive) / len(gold_tags)
        f1 = 2 * precision * recall / (precision + recall)
        rp.print("True positive: {}".format(len(true_positive)))
        rp.print("Gold # senses: {}".format(len(gold_tags)))
        rp.print("Predicted # senses: {}".format(len(profile_tags)))
        rp.print("Precision: {:.2f}%".format(precision * 100))
        rp.print("Recall   : {:.2f}%".format(recall * 100))
        rp.print("F1       : {:.2f}%".format(f1 * 100))


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ChirpText Tools main function '''
    app = CLIApp(desc='ISF TTL Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('cmp', func=compare_ttls)
    task.add_argument('-g', '--gold_profile', help='Gold Profile', default=None)
    task.add_argument('-p', '--profile', help='Profile for evaluation', default=None)
    # run app
    app.run()


if __name__ == "__main__":
    main()
