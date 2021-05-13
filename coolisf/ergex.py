# -*- coding: utf-8 -*-

"""
Extracting MWE from ERG's lexicon
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import codecs
import re
import logging
from collections import defaultdict
import csv

from texttaglib.chirptext.leutile import Counter
from texttaglib.chirptext.leutile import FileHelper
from texttaglib.chirptext.leutile import TextReport
from texttaglib.chirptext.leutile import FileHub
from texttaglib.chirptext.leutile import Timer
from texttaglib.chirptext.leutile import header

from yawlib import YLConfig
from yawlib import WordnetSQL as WNSQL
from coolisf.mappings import PredSense


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

MWE_NOTFOUND = os.path.expanduser('data/mwe_notfound.txt')
MWE_FOUND = os.path.expanduser('data/mwe_found.txt')
MWE_PRED_LEMMA = os.path.expanduser('data/mwe_pred_lemma.txt')
LEXDB = FileHelper.abspath('data/lexdb.rev')
ERG_LEX_FILE = FileHelper.abspath('data/lexicon.tdl')
ERG_PRED_FILE = FileHelper.abspath('data/ergpreds.py')
ERG_PRED_NOT_FOUND_FILE = FileHelper.abspath("data/ergpreds_not_mapped.txt")
ERG_PRED_FILE_TEMPLATE = open(FileHelper.abspath('data/ergpreds.template.py'), 'r').read()


def getLogger():
    return logging.getLogger(__name__)


class ERGLex:

    def __init__(self, name, userid, modstamp, dead, lextype, orthography, nagreement, keyrel, altkey, alt2key, keytag,
                 altkeytag, compkey, ocompkey, pronunciation, complete, semclasses, preferences,
                 classifier, selectrest, jlink, comments, exemplars, usages, lang, country, dialect, domains, genres, register, confidence, source):
        # user defined
        # LexDbFieldMappings >>> HOW TO create initial .fld file (first 4 columns are name, userid, modstamp, dead)
        self.name = name
        self.userid = userid
        self.modstamp = modstamp
        self.dead = (False if dead == 'f' else True)
        # the rest in lexdb.fld
        self.lextype = self.parse_text(lextype)
        self.orthography = self.parse_text(orthography)
        self.nagreement = self.parse_text(nagreement)
        self.keyrel = self.parse_text(keyrel)
        self.altkey = self.parse_text(altkey)
        self.alt2key = self.parse_text(alt2key)
        self.keytag = self.parse_text(keytag)
        self.altkeytag = self.parse_text(altkeytag)
        self.compkey = self.parse_text(compkey)
        self.ocompkey = self.parse_text(ocompkey)
        self.pronunciation = self.parse_text(pronunciation)
        self.complete = self.parse_text(complete)
        self.semclasses = self.parse_text(semclasses)
        self.preferences = self.parse_text(preferences)
        self.classifier = self.parse_text(classifier)
        self.selectrest = self.parse_text(selectrest)
        self.jlink = self.parse_text(jlink)
        self.comments = self.parse_text(comments)
        self.exemplars = self.parse_text(exemplars)
        self.usages = self.parse_text(usages)
        self.lang = self.parse_text(lang)
        self.country = self.parse_text(country)
        self.dialect = self.parse_text(dialect)
        self.domains = self.parse_text(domains)
        self.genres = self.parse_text(genres)
        self.register = self.parse_text(register)
        self.confidence = self.parse_text(confidence)
        self.source = self.parse_text(source)

    def __repr__(self):
        return self.keyrel

    def parse_text(self, value):
        return value if value != '\\N' else ''

    def __str__(self):
        fields = ("{}={}".format(k, repr(v)) for k, v in self.__dict__.items() if v)
        return "ERGLex({})".format(", ".join(fields))


def to_sense_map(k, v):
    sinfos = ["SenseInfo('{sid}', {tc})".format(sid=x.sid, tc=x.tagcount) for x in v]
    return '"%s" : [ %s ]' % (k, ", ".join(sinfos))


def read_erg_lex():
    if not os.path.isfile(LEXDB):
        getLogger().error("ERG DB cannot be found")
        return []
    with open(LEXDB, 'r') as lexdb:
        rows = list(csv.reader(lexdb, delimiter='\t'))
    return [ERGLex(*row) for row in rows]


def dev():
    # TODO: Something is wrong with _pass_v_along ...
    #keyrels = [ "_give_v_off_rel", "give_v_off_rel", "_pass_v_along_rel", "pass_v_along_rel" ]
    #for kr in keyrels:
    #    senses = PredSense.search_pred_string(kr)
    #    delphin_pred = Pred.grammarpred(kr)
    #    print("%s (delphin=%s) => %s" % (kr, delphin_pred.lemma, senses))
    #print("-" * 20)
    #return

    outfiles = FileHub('.txt')
    lexs = read_erg_lex()
    c = Counter()
    lpsr_pattern = re.compile(r"_?[a-zA-Z0-9\-\+\\\/\$]+_[a-zA-Z]+_[0-9]+_rel")  # _dog_n_1_rel
    lpr_pattern = re.compile(r"_?[a-zA-Z\-\+\\]+_[a-zA-Z]+_rel")  # _dog_n_rel
    lr_pattern = re.compile(r"_?[a-zA-Z0-9\-\+\\]+_rel")  # person_rel
    llr_pattern = re.compile(r"_?[a-zA-Z\-\+\\]+_[a-zA-Z\-\+\\]+_rel")  # comp_not+so_rel
    lplr_pattern = re.compile(r"_?[a-zA-Z\-\+\\]+_[a-zA-Z]+_[a-zA-Z0-9\+\-]+_rel")  # _abate_v_cause_rel
    # Create output files
    outfiles.create('data/ergpreds_lpsr')
    outfiles.create('data/ergpreds_lpr')
    outfiles.create('data/ergpreds_lr')
    outfiles.create('data/ergpreds_llr')
    outfiles.create('data/ergpreds_lplr')
    outfiles.create('data/ergpreds_unknown')

    found_preds = set()
    for lex in lexs:
        c.count("Total")
        if lex.keyrel == '\\N':
            c.count("\\N")
        elif lpsr_pattern.match(lex.keyrel):
            if lex.keyrel not in found_preds: outfiles.writeline('data/ergpreds_lpsr', lex.keyrel)
            c.count("_lemma_pos_senseno_rel")
        elif lpr_pattern.match(lex.keyrel):
            if lex.keyrel not in found_preds: outfiles.writeline('data/ergpreds_lpr', lex.keyrel)
            c.count("_lemma_pos_rel")
        elif lr_pattern.match(lex.keyrel):
            if lex.keyrel not in found_preds: outfiles.writeline('data/ergpreds_lr', lex.keyrel)
            c.count("_lemma_rel")
        elif llr_pattern.match(lex.keyrel):
            if lex.keyrel not in found_preds: outfiles.writeline('data/ergpreds_llr', lex.keyrel)
            c.count("_lemma_suplem_rel")
        elif lplr_pattern.match(lex.keyrel):
            if lex.keyrel not in found_preds: outfiles.writeline('data/ergpreds_lplr', lex.keyrel)
            c.count("_lemma_pos_suplem_rel")
        else:
            if lex.keyrel not in found_preds: outfiles.writeline('data/ergpreds_unknown', lex.keyrel)
            c.count("UNKNOWN")
        found_preds.add(lex.keyrel)
    print(len(found_preds))
    outfiles.close()
    c.summarise()
    print("-" * 20)


def extract_all_rel():
    # report header
    t = Timer()
    report = TextReport(ERG_PRED_FILE)
    senses_map = defaultdict(list)
    c = Counter()

    t.start("Extracting preds from ERG")
    lex_entries = read_erg_lex()
    t.end()

    t.start("Mapping those to wordnet senses")
    for lex in lex_entries:
        c.count('Entry')
        if lex.keyrel != '\\N':
            if not lex.keyrel.endswith('_rel'):
                c.count('WARNING')
                print(lex.keyrel)
            else:
                senses = PredSense.search_pred_string(lex.keyrel)
                senses_map[lex.keyrel] += senses
                # if lex.keyrel == '_pass_v_along_rel':
                #    print("%s => %s" % (lex.keyrel, senses))
    t.end()

    t.start("Saving predlinks to file")
    report.print(ERG_PRED_FILE_TEMPLATE)
    report.print("ERG_PRED_MAP = {")
    senses_list = [to_sense_map(k, v) for k, v in senses_map.items()]
    report.print(",\n".join(senses_list))
    report.print("}")
    c.summarise()
    report.close()
    t.end("Mapping info has been written to %s" % (ERG_PRED_FILE,))

    # Investigate senses that can't be mapped
    not_mapped_file = TextReport(ERG_PRED_NOT_FOUND_FILE)
    mc = Counter()  # Mapped count

    maxlength = 0
    for k in senses_map.keys():
        if len(k) > maxlength:
            maxlength = len(k)

    for k, v in senses_map.items():
        if not v:
            tracer = []
            PredSense.search_pred_string(k, tracer=tracer)
            not_mapped_file.print("%s [Search info: %s]" % (k.ljust(maxlength + 1), tracer))
            mc.count("Not Mapped")
        else:
            mc.count("Mapped")
        mc.count("Total")
    not_mapped_file.close()

    header("Mapping Information")
    mc.summarise()

    print("Mapped     >>> %s" % (ERG_PRED_FILE,))
    print("Not Mapped >>> %s" % (ERG_PRED_NOT_FOUND_FILE,))
    pass


def find_mwe():
    mwe_list = set()

    getLogger().info("Extracting MWE from ERG's lexicon")
    if not os.path.isfile(ERG_LEX_FILE):
        getLogger().warning("ERG lexicon file could not be found at {}".format(ERG_LEX_FILE))
    else:
        with codecs.open(ERG_LEX_FILE, 'r', encoding='utf-8') as erg:
            mwe = None
            for l in erg:
                if ':=' in l:
                    m = re.match(r"([a-z_]+)_v[0-9]+ := v_p[_-]", l)
                    if m:
                        ms = m.group(1).split('_')
                        mwe = " ".join(ms)
                    else:
                        mwe = None
                if mwe:
                    mm = re.search(r"KEYREL.PRED \"([-a-z_]+)\"", l)
                    if mm:
                        mwe_list.add((mwe, mm.group(1)))
    return mwe_list


def extract_mwe():
    print("Loading WordNet ...")
    all_senses = WNSQL(YLConfig.WNSQL30_PATH).all_senses()
    mwe_list = find_mwe()
    # Searching for lexicon
    print("Mapping to WordNet ...")
    c = Counter()
    mwe_found = []
    mwe_notfound = []
    for mwe in mwe_list:
        getLogger().debug("Looking for [%s]" % (mwe[0],))
        if mwe[0] in all_senses:
            candidates = all_senses[mwe[0]]
            mwe_found.append(',"%s"' % (mwe[1],) + ': [' + ', '.join(('"%s"' % (x.sid) for x in candidates)) + "] # " + mwe[0])
            c.count("Found")
        else:
            c.count("Not found")
            mwe_notfound.append('\t'.join(mwe))
        c.count("Total")
    c.summarise()
    mwe_found = ['# This file contains predicates in ERG which have been mapped to concept in WordNet', '# '] + mwe_notfound
    FileHelper.save(MWE_FOUND, '\n'.join(mwe_found))
    mwe_notfound = ['# This file contains predicates in ERG which could not be found in WordNet', '# '] + mwe_notfound
    FileHelper.save(MWE_NOTFOUND, '\n'.join(mwe_notfound))
    pred_lemma = ['# This file contains all VV preds in ERG and their lemmas', "# "]
    pred_lemma += [",'%s' : '%s'" % (x[1], x[0]) for x in mwe_list]
    FileHelper.save(MWE_PRED_LEMMA, '\n'.join(pred_lemma))
    print("All done")
    pass


def main():
    # dev()
    extract_mwe()
    extract_all_rel()


if __name__ == "__main__":
    main()
