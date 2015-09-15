#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Extracting MWE from ERG's lexicon

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

# Copyright (c) 2015, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2015, intsem.fx"
__credits__ = [ "Le Tuan Anh" ]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import codecs
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom

from delphin.interfaces import ace
from delphin.mrs.components import Pred

from chirptext.leutile import StringTool
from chirptext.leutile import Counter
from chirptext.texttaglib import writelines
from lelesk import WSDResources
from lelesk import WSDResources

from .model import Sentence
from .util import PredSense

########################################################################

MWE_NOTFOUND = os.path.expanduser('data/mwe_notfound.txt')
MWE_FOUND = os.path.expanduser('data/mwe_found.txt')
MWE_PRED_LEMMA = os.path.expanduser('data/mwe_pred_lemma.txt')

def main():
    print("Loading WordNet ...")
    all_senses = WSDResources.singleton(True).wnsql.all_senses()
    
    print("Extracting MWE from ERG's lexicon")
    erg = codecs.open(os.path.expanduser("~/logon/lingo/erg/lexicon.tdl"), 'r', encoding='utf-8')
    pvs = set()
    prt = set()
    mwe = None
    mwe_list = set()
    mwe_lemma_map = {}
    for l in erg:
        if ':=' in l:
            m = re.match(r"([a-z_]+)_v[0-9]+ := v_p[_-]", l)
        
            if m:
                ms = m.group(1).split('_')
                # print "%s\t%s" % (ms, m)
                mwe = " ".join(ms)
                #if len(ms) > 2:
                #   print(mwe)
            else:
                mwe = None
        if mwe: 
            mm = re.search(r"KEYREL.PRED \"([-a-z_]+)\"", l)
            
            if mm:
                # print("%s\t%s" % (mwe, mm.group(1)))
                mwe_list.add((mwe, mm.group(1)))
                mwe_lemma_map[mm.group(1)] = mwe
    with open('data/mwe.txt', 'w') as outfile:
        for mwe in mwe_list:
            outfile.write('\t'.join(mwe))
            outfile.write('\n')
            
    # Searching for lexicon
    print("Mapping to WordNet ...")
    c = Counter()
    mwe_found = []
    mwe_notfound = []
    for mwe in mwe_list:
        print("Looking for [%s]" % (mwe[0],))
        if mwe[0] in all_senses:
            candidates = all_senses[mwe[0]]
            mwe_found.append(',"%s"' % (mwe[1],) + ': [' + ', '.join(('"%s-%s"' % (str(x.sid)[1:], x.pos) for x in candidates)) + "] # " + mwe[0])
            c.count("Found")
        else:
            c.count("Not found")
            mwe_notfound.append('\t'.join(mwe))
        c.count("Total")
    c.summarise()
    mwe_found = [ '# This file contains predicates in ERG which have been mapped to concept in WordNet', '# ' ] + mwe_notfound
    writelines(mwe_found, MWE_FOUND)
    mwe_notfound = [ '# This file contains predicates in ERG which cannot be found in WordNet', '# ' ] + mwe_notfound
    writelines(mwe_notfound, MWE_NOTFOUND)
    pred_lemma =  [ '# This file contains all VV preds in ERG and their lemmas', "# " ]
    pred_lemma += [ ",'%s' : '%s'" % (x[1], x[0]) for x in mwe_list ] 
    writelines(pred_lemma, MWE_PRED_LEMMA)
    print("All done")
    pass

if __name__ == "__main__":
    main()
