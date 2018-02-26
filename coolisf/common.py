# -*- coding: utf-8 -*-

'''
Common functions

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    ACE:
        http://moin.delph-in.net/AceOptions

@author: Le Tuan Anh <tuananh.ke@gmail.com>
@license: MIT
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

########################################################################

import os
import gzip
import logging

from chirptext import FileHelper


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def read_file(file_path, mode='rt'):
    file_path = FileHelper.abspath(file_path)  # normalize path
    if not os.path.isfile(file_path):
        raise Exception("Input file not found: {}".format(file_path))
    if file_path.endswith('.gz'):
        with gzip.open(file_path, mode) as infile:
            return infile.read()
    else:
        return FileHelper.read(file_path, mode)


def write_file(content, outpath=None):
    ''' Write content to a file, or to console if no path is provided '''
    if isinstance(content, str):
        mode = 'wt'
    else:
        mode = 'wb'
    if outpath:
        getLogger().debug("Writing content to {}".format(outpath))
        if outpath.endswith('.gz'):
            with gzip.open(outpath, mode) as outfile:
                outfile.write(content)
        else:
            with open(outpath, mode) as outfile:
                outfile.write(content)
    else:
        print(content)


def overlap(cfrom1, cto1, cfrom2, cto2):
    if cfrom1 is None or cto1 is None or cfrom2 is None or cto2 is None:
        raise ValueError("cfrom:cto must be numbers")
    return (cfrom1 <= cfrom2 < cto1) or (cfrom2 <= cfrom1 < cto2)


def tags_to_concepts(sent):
    ''' Take concepts from sentence-level tags and create token-level concepts '''
    for tag in sent.tags:
        tokens = [tk for tk in sent.tokens if overlap(tag.cfrom, tag.cto, tk.cfrom, tk.cto)]
        if tokens:
            sent.new_concept(tag.label, tokens=tokens)
    return sent


def ptpos_to_wn(ptpos):
    ''' Penn Treebank Project POS to WN '''
    # Ref: http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    # CC Coordinating conjunction
    # CD Cardinal number
    # DT Determiner
    # EX Existential there
    # FW Foreign word
    # IN Preposition or subordinating conjunction
    # -----------------------------
    # JJ Adjective
    # JJR Adjective, comparative
    # JJS Adjective, superlative
    # -----------------------------
    # LS List item marker
    # MD Modal
    # -----------------------------
    # NN Noun, singular or mass
    # NNS Noun, plural
    # NNP Proper noun, singular
    # NNPS Proper noun, plural
    # -----------------------------
    # PDT Predeterminer
    # POS Possessive ending
    # PRP Personal pronoun
    # PRP$ Possessive pronoun
    # -----------------------------
    # RB Adverb
    # RBR Adverb, comparative
    # RBS Adverb, superlative
    # -----------------------------
    # RP Particle
    # SYM Symbol
    # TO to
    # UH Interjection
    # -----------------------------
    # VB Verb, base form
    # VBD Verb, past tense
    # VBG Verb, gerund or present participle
    # VBN Verb, past participle
    # VBP Verb, non­3rd person singular present
    # VBZ Verb, 3rd person singular present
    # -----------------------------
    # WDT Wh­determiner
    # WP Wh­pronoun
    # WP$ Possessive wh­pronoun
    # WRB Wh­adverb
    if ptpos.startswith('JJ'):
        return 'a'
    elif ptpos.startswith('NN'):
        return 'n'
    elif ptpos.startswith('RB'):
        return 'r'
    elif ptpos.startswith('VB'):
        return 'v'
    else:
        return 'x'
