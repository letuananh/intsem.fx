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

from chirptext import TextReport
from chirptext.cli import CLIApp, setup_logging
from chirptext import texttaglib as ttl

from coolisf.gold_extract import read_gold_mrs

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

def fix_gold(cli, args):
    sents = read_gold_mrs()
    doc = ttl.Document('gold', 'data/').read()
    patches = []
    for s in sents:
        tagged = doc.sent_map[str(s.ident)]
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


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    ''' ISF Gold miner '''
    app = CLIApp(desc='ISF Gold mining Toolkit', logger=__name__)
    # add tasks
    task = app.add_task('fix', func=fix_gold)
    task.add_argument('-o', '--output', help='Output file', default=None)
    # run app
    app.run()


if __name__ == "__main__":
    main()
