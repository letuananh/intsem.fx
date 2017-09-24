# -*- coding: utf-8 -*-

'''
Utility functions

Latest version can be found at https://github.com/letuananh/intsem.fx

References:
    Python documentation:
        https://docs.python.org/
    ACE:
        http://moin.delph-in.net/AceOptions
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import re
import logging
from chirptext import Counter, FileHelper
from coolisf.model import Sentence


##########################################
# CONFIGURATION
##########################################

MY_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(MY_DIR, 'config.json')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


########################################################################

def read_ace_output(ace_output_file):
    ''' Read output file from ACE batch mode
    Sample command: ace -g grammar.dat infile.txt > outfile.txt
    Read more: http://moin.delph-in.net/AceOptions
    '''
    logger.info("Reading parsed MRS from %s..." % (ace_output_file,))
    c = Counter()
    items = []
    sentences = []
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
                sentences.append(s)
                while mrs_line.strip():
                    s.add(mrs_line)
                    mrs_line = input_mrs.readline()
                input_mrs.readline()
                c.count('sent')
                c.count('total')
            elif line.startswith('SKIP'):
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
    return sentences


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
