#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###
### Read in the ERG's lexicon and try to make new entries with senses
###
### Francis Bond
###
### ToDo
### * MWEs
### * NTUMC-WN
### * valency check
### 

## Usage
## lex2wn.py > mapping

import os
from delphin import tdl
from coolisf.mappings import PredSense

lex = 'data/lexicon.tdl'
if not os.path.isfile(lex):
    print("data/lexicon.tdl is required")
    exit()
log = open('lex2wn.log', 'w')

f = open(lex, 'r')

for l in tdl.parse(f):
    lid=l.identifier
    if 'SYNSEM' in [f for (f,v) in l.features()]:
        if 'LKEYS.KEYREL.PRED' in [f for (f,v) in l['SYNSEM'].features()]:
            if isinstance(l['SYNSEM']['LKEYS.KEYREL.PRED'],str):
                pred = l['SYNSEM']['LKEYS.KEYREL.PRED']
                synsets = PredSense.search_pred_string(pred)
                for ss in synsets:
                    print (lid, ss.synsetid,ss.lemmas)
                    print ('# {}\n'.format("; ".join(ss.defs)))
                else:
                    print ('No synsets for {}, {}, {}'.format(repr(l.identifier), repr(pred), repr(synsets)),
                           file=log)
            else:
                ### how do I get the type?
                # print(l.identifier,
                #       l['SYNSEM']['LKEYS.KEYREL.PRED'],
                #       l['SYNSEM']['LKEYS.KEYREL.PRED'].features(),
                #       l['SYNSEM']['LKEYS.KEYREL.PRED'].type)
                print ('LKEYS.KEYREL.PRED is type for {}'.format(lid), file=log)
        else:
            print ('No LKEYS.KEYREL.PRED for {}'.format(l.identifier), file=log)
    else:
        print ('No SYNSEM for {}'.format(l.identifier), file=log)
#    print (l.identifier, l.features(),l['SYNSEM'].features())
