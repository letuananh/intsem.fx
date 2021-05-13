# -*- coding: utf-8 -*-

"""
Utility functions
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import re
import logging

from texttaglib.chirptext import Counter, FileHelper

from coolisf.model import Sentence, Document


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

MY_DIR = os.path.dirname(os.path.abspath(__file__))


def getLogger():
    return logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def read_ace_output(ace_output_file, top1dmrs=False):
    """ Read output file from ACE batch mode
    Sample command: ace -g grammar.dat infile.txt > outfile.txt
    Read more: http://moin.delph-in.net/AceOptions
    """
    getLogger().info("Reading parsed MRS from %s..." % (ace_output_file,))
    c = Counter()
    items = []
    doc = Document(name=FileHelper.getfilename(ace_output_file))
    skipped = []
    with open(ace_output_file, 'r') as input_mrs:
        current_sid = 0
        while True:
            current_sid += 1
            line = input_mrs.readline()
            if line.startswith('SENT'):
                mrs_line = input_mrs.readline()
                # item = [line, mrs_line]
                s = Sentence(line[5:], ID=current_sid)
                doc.add(s)
                if not top1dmrs:
                    while mrs_line.strip():
                        s.add(mrs_line)
                        mrs_line = input_mrs.readline()
                    input_mrs.readline()
                else:
                    # all lines = a single DMRS
                    dmrs_text = ''
                    while mrs_line.strip():
                        dmrs_text += mrs_line
                        mrs_line = input_mrs.readline()
                    input_mrs.readline()
                    s.add(dmrs_text)
                c.count('sent')
                c.count('total')
            elif line.startswith('SKIP'):
                s = Sentence(line[5:], ID=current_sid)
                doc.add(s)
                skipped.append(line[5:].strip())
                items.append([line])
                input_mrs.readline()
                input_mrs.readline()
                c.count('skip')
                c.count('total')
            else:
                break
    c.summarise()
    FileHelper.save(ace_output_file + '.skipped.txt', '\n'.join(skipped))
    return doc


def sent2json(sent, sentence_text=None, parse_count=-1, tagger='N/A', grammar='N/A'):
    xml_str = sent.to_xml_str()
    sent_json = {'sent': sentence_text if sentence_text else sent.text,
                 'parse_count': parse_count,
                 'tagger': tagger,
                 'grammar': grammar,
                 'parses': [parse2json(x) for x in sent],
                 'xml': xml_str,
                 'latex': sent.to_latex(),
                 'shallow': sent.shallow.to_json() if sent.shallow else {}}
    if sent.flag is not None:
        sent_json['flag'] = sent.flag
    if sent.comment is not None:
        sent_json['comment'] = sent.comment
    return sent_json


def parse2json(parse):
    return {'pid': parse.ID,
            'ident': parse.rid,
            'mrs': parse.mrs().json(),
            'dmrs': parse.dmrs().json(),
            'mrs_raw': parse.mrs().tostring(),
            'dmrs_raw': parse.dmrs().tostring()}


# only alphanumeric characters are accepted in names
NAME_RE = re.compile('^[A-Za-z0-9_]+$')


def is_valid_name(a_name):
    return NAME_RE.match(str(a_name)) if a_name is not None else False
