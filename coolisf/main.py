#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Integrated Semantic Framework (coolisf) main application

`coolisf` is read `kul-eye-es-ef` officially (sometimes kul-is-f)
'''

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import logging
import collections

from texttaglib.chirptext.cli import CLIApp, setup_logging
from texttaglib.chirptext import header, confirm, TextReport, FileHelper, Counter, Timer
from texttaglib.chirptext.leutile import is_number
from texttaglib.chirptext import texttaglib as ttl
from lelesk import LeLeskWSD
from lelesk import LeskCache  # WSDResources

from coolisf import __version__
from coolisf.lexsem import Lexsem
from coolisf.config import read_config, _get_config_manager
from coolisf.common import write_file
from coolisf.morph import Transformer
from coolisf.ghub import GrammarHub
from coolisf.util import read_ace_output
from coolisf.dao import read_tsdb
from coolisf.gold_extract import read_tsdb_ttl, tag_doc
from coolisf.gold_extract import generate_gold_profile
from coolisf.gold_extract import export_to_visko
from coolisf.gold_extract import read_gold_sents
from coolisf.model import Document
from coolisf.dao.textcorpus import RawCollection
from coolisf.mappings import PredSense


OUTPUT_DMRS = 'dmrs'
OUTPUT_MRS = 'mrs'
OUTPUT_XML = 'xml'
OUTPUT_FORMATS = [OUTPUT_DMRS, OUTPUT_MRS, OUTPUT_XML]
WSD_CHOICES = [ttl.Tag.LELESK, ttl.Tag.MFS]
setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)

########################################################################


def to_visko(cli, args):
    ''' Convert ACE output to ISF XML format '''
    # determine docpath
    if args.bibloc:
        visko_data_dir = os.path.abspath(args.bibloc)
    else:
        # default bibloc
        visko_data_dir = os.path.expanduser('~/workspace/visualkopasu/data/biblioteche')
    if args.separate:
        export_path = os.path.join(visko_data_dir, args.biblioteca, args.corpus, args.doc)
    else:
        export_path = args.doc
    print("Biblioteche location: {}".format(visko_data_dir))
    print("Document location   : {}".format(export_path))
    # which file to export
    if args.file is not None:
        # export MRS file
        sents = read_ace_output(args.file, top1dmrs=args.top1dmrs)  # e.g. data/wndefs.nokey.mrs.txt
        if args.topk:
            sents = sents[:int(args.topk)]
    else:
        if input("No MRS file provided. Proceed to export gold profile to Visko (yes/no)? ").lower() in ['y', 'yes']:
            print("Exporting gold profile to Visko")
            sents = read_gold_sents()
        else:
            print("Aborted")
            return
    export_to_visko(sents, export_path, separate=args.separate, halt_on_error=not args.forgive)


def parse_isf(cli, args):
    ''' Process raw text file '''
    # verification
    if not os.path.isfile(args.infile):
        print("Error. File does not exist. (provided: {})".format(args.infile))
    if args.output and os.path.exists(args.output):
        if not confirm("Output file exists. Do you want to continue (Y/N)? "):
            print("Program aborted.")
            return
    # process
    header("Processing file: {}".format(args.infile))
    report = TextReport(args.output)
    ghub = GrammarHub()
    lines = FileHelper.read(args.infile).splitlines()
    wsd = LeLeskWSD(dbcache=LeskCache())
    ctx = PredSense.wn.ctx()
    timer = Timer(cli.logger)
    timer.start("Parsing {} sentences".format(len(lines)))
    for idx, sent in enumerate(ghub.ERG_ISF.parse_many_iterative(lines, parse_count=args.topk, ignore_cache=args.nocache)):
        if args.max and args.max < idx:
            break
        print("Processing sentence {} of {}".format(idx + 1, len(lines)))
        sent.tag_xml(method=args.wsd, wsd=wsd, ctx=ctx)
        report.writeline(sent.to_xml_str(pretty_print=not args.compact))
        report.writeline("\n\n")
    timer.stop("Finished")


def retag_doc(cli, args):
    ''' Re-tag an ISF document '''
    # verification
    if args.output and os.path.exists(args.output) and not args.yes:
        if not confirm("Output file exists. Do you want to continue (Y/N)? "):
            print("Program aborted.")
            return
    # process
    header("Processing file: {}".format(args.path))
    doc = Document.from_file(args.path, idents=args.ident)
    print("Document size: {}".format(len(doc)))
    if not args.wsd and not args.ttl:
        print("Nothing to do")
        return
    if args.wsd:
        print("Retagging document using {}".format(args.wsd))
        wsd = LeLeskWSD(dbcache=LeskCache())
        wsd.connect()
        ctx = PredSense.wn.ctx()
        for idx, sent in enumerate(doc):
            if args.topk and idx > args.topk:
                break
            if args.ident and sent.ident not in args.ident:
                continue
            print("Tagging sentence #{}/{}".format(idx + 1, len(doc)))
            try:
                sent.tag_xml(method=args.wsd, wsd=wsd, ctx=ctx)
            except Exception as e:
                if args.forgive:
                    getLogger().warning("Could not process sentence {}".format(sent.ID))
                else:
                    raise e
        ctx.close()
        wsd.disconnect()
    if args.ttl:
        print("Tagging doc {} using TTL doc {}".format(doc.name, args.ttl))
        ttl_doc = ttl.read(args.ttl, mode=args.ttl_format)
        kwargs = {}
        if args.mode:
            kwargs['mode'] = args.mode
        tag_doc(doc, ttl_doc, taggold=not args.nogold, on_error=args.on_error, **kwargs)
    doc_xml_str = doc.to_xml_str(pretty_print=not args.compact, with_dmrs=not args.nodmrs)
    write_file(doc_xml_str, args.output)


def extract_tsdb(cli, args):
    ''' Read parsed sentences from a TSDB profile '''
    if not os.path.exists(args.path):
        print("TSDB profile does not exist (path: {})".format(args.path))
    else:
        # read document
        timer = Timer(cli.logger)
        timer.start("Reading document")
        if os.path.isdir(args.path):
            # is TSDB
            if args.ttl:
                doc = read_tsdb_ttl(args.path, ttl_path=args.ttl, name=args.name, title=args.title)
            else:
                doc = read_tsdb(args.path)
            if args.ident or args.ids:
                print("Idents: {}".format(args.ident))
                doc_new = Document(name=doc.name, title=doc.title)
                for sent in doc:
                    if (sent.ident in args.ident) or (sent.ID in args.ids):
                        doc_new.add(sent)
                doc = doc_new
        elif os.path.isfile(args.path):
            # read doc XML
            doc = Document.from_file(args.path, idents=args.ident)
            print(len(doc))
            if args.ttl:
                ttl_doc = ttl.Document.read_ttl(args.ttl)
                doc = tag_doc(doc, ttl_doc)
        # process doc
        print("Found sentences: {}".format(len(doc)))
        print("With shallow: {}".format(len(list(s for s in doc if s.shallow))))
        timer.stop("Reading document")
        if args.isf:
            print("performing ISF transformation")
            transformer = Transformer()
            total = len(doc)
            for idx, sent in enumerate(doc):
                print("Processing {} of {} sentences".format(idx + 1, total))
                try:
                    transformer.apply(sent)
                except:
                    getLogger().warning("Cannot transform sentene {}".format(sent.ID))
                if args.topk and int(args.topk) < idx:
                    break
        timer.stop("ISF transformation")
        # perform WSD if required
        if args.wsd:
            print("Performing WSD using {}...".format(args.wsd))
            wsd = LeLeskWSD(dbcache=LeskCache())
            ctx = PredSense.wn.ctx()
            for idx, sent in enumerate(doc):
                print("processed {} of {} sentences".format(idx + 1, len(doc)))
                sent.tag_xml(method=args.wsd, wsd=wsd, ctx=ctx)
                if args.topk and int(args.topk) < idx:
                    break
            ctx.close()
            timer.stop("WSD ({})".format(args.wsd))
        print("Generating output ...")
        doc_xml_str = doc.to_xml_str(pretty_print=not args.compact, with_dmrs=not args.nodmrs)
        write_file(doc_xml_str, args.output)
        timer.stop("Finished")


def parse_text(cli, args):
    ''' Analyse a text '''
    ghub = GrammarHub()
    text = args.input
    wsd = LeLeskWSD(dbcache=LeskCache())
    ctx = PredSense.wn.ctx()
    timer = Timer(logger=cli.logger)
    timer.start("Parsing \"{}\"".format(text))
    result = ghub.parse(text, args.grammar, args.topk, args.wsd, args.nocache, wsd=wsd, ctx=ctx)
    if result is not None and len(result) > 0:
        report = TextReport(args.output)
        if args.format == OUTPUT_DMRS:
            report.header(result)
            for reading in result:
                report.writeline(reading.dmrs().tostring(pretty_print=not args.compact))
                if reading.dmrs().tags:
                    for nodeid, tags in reading.dmrs().tags.items():
                        tag_str = ', '.join('{}[{}/{}]'.format(s.ID, s.lemma, m) for s, m in tags)
                        report.writeline("# {} -> {}".format(nodeid, tag_str))
                report.writeline()
        elif args.format == OUTPUT_XML:
            result.tag_xml()
            report.writeline(result.to_xml_str(pretty_print=not args.compact))
        elif args.format == OUTPUT_MRS:
            report.header(result)
            for reading in result:
                report.writeline(reading.mrs().tostring(pretty_print=not args.compact))
                report.writeline()
        if args.shallow and result.shallow is not None:
            shallow = result.shallow
            report.writeline(shallow.tokens)
            for concept in shallow.concepts:
                if concept.comment:
                    report.writeline("{} - {}".format(concept, concept.comment))
                else:
                    report.writeline("{} - {}".format(concept, concept.comment))
    timer.stop("Text: {} | Parses: {}".format(text, len(result)))


def parse_bib(cli, args):
    ''' Parse a complete biblioteca '''
    c = Counter()
    ghub = GrammarHub()
    bib_path = FileHelper.abspath(args.input)
    if not os.path.isdir(bib_path):
        cli.logger.warning("Raw biblioteca could not be found at {}".format(bib_path))
        exit()
    cli.logger.info("Analysing biblioteca {}".format(bib_path))
    # validate output
    if not args.output or not os.path.isdir(args.output):
        cli.logger.warning("Output directory does not exist")
        exit()
    bib = RawCollection(bib_path)
    corpuses = bib.get_corpuses()
    print("Available corpuses: {}".format(len(corpuses)))
    c.update({"Corpuses": len(corpuses)})
    for corpus in corpuses:
        print("Processing corpus: {} ({})".format(corpus.name, corpus.title))
        # create dir for corpus
        corpus_path = os.path.join(args.output, corpus.name)
        if not os.path.exists(corpus_path):
            os.makedirs(corpus_path)
        for doc in corpus.get_documents():
            c.count("Documents")
            sents = list(doc.read_sentences())
            c.update({'Sentences': len(sents)})
            print("Processing document: {} {} | Size: {}".format(doc.name, doc.title, len(sents)))
            doc_path = os.path.join(corpus_path, doc.name + '.xml')
            doc_isf = Document(name=doc.name, title=doc.title)
            sent_texts = [s.text for s in sents]
            # parse document
            report = TextReport(doc_path)
            for sent in ghub.ERG_ISF.parse_many_iterative(sent_texts, parse_count=args.topk, ignore_cache=args.nocache):
                sent.tag_xml(method=args.wsd)
                print("Processed: {}".format(sent.text))
                doc_isf.add(sent)
            report.writeline(doc_isf.to_xml_str(pretty_print=not args.compact))
    c.summarise()


def export_ttl(cli, args):
    ''' Export ISF document to TTL '''
    doc = Document.from_file(args.path)
    print("Found MRS {} sentences".format(len(doc)))
    if args.output:
        out_name = os.path.basename(args.output)
        if out_name.endswith('.ttl.json'):
            out_name = out_name[:-9]
        if out_name.endswith('.ttl.json.gz'):
            out_name = out_name[:-12]
    else:
        out_name = 'ttl_output'
    print("TTL mode: {}".format(args.ttl_format))
    if args.ttl_format == ttl.MODE_JSON:
        _writer = ttl.JSONWriter.from_path(args.output)
    else:
        _writer = ttl.TxtWriter.from_path(args.output)
    empty_sents = []
    written_count = 0
    tag_count = 0
    print("Exporting ISF document to TTL - Empty sentences will be removed automatically")
    for idx, sent in enumerate(doc):
        sent_id = sent.ident if sent.ident else sent.ID if is_number(sent.ID) else idx
        tsent = ttl.Sentence(text=sent.text, ID=sent_id)
        if not len(sent):
            empty_sents.append(sent_id)
            continue
        dmrs = sent[0].dmrs()  # only support the first reading for now
        tags = dmrs.find_tags()
        for nid, ss in tags.items():
            node = dmrs.layout[nid]
            synsets = {(s.ID, tuple(s.lemmas), m) for s, m in ss}
            for synsetid, lemmas, method in synsets:
                tsent.new_tag(synsetid.to_canonical(), node.cfrom, node.cto, tagtype='WN')
                tag_count += 1
                if args.with_lemmas:
                    tsent.new_tag(','.join(lemmas), node.cfrom, node.cto, tagtype='WN-LEMMAS')
        written_count += 1
        _writer.write_sent(tsent)
    print("Created {} tags".format(tag_count))
    if empty_sents:
        print("Empty sentences: {}/{}".format(len(empty_sents), len(doc)))
        if args.emptyfile:
            ef = TextReport(args.emptyfile)
            for sid in empty_sents:
                ef.print(sid)
    print("Written sentences: {}".format(written_count))
    print("Output: {}".format(FileHelper.abspath(args.output)))
    _writer.close()
    print("Done!")


def isf_config_logging(args):
    if args.quiet:
        logging.getLogger().setLevel(logging.CRITICAL)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('coolisf.ghub').setLevel(logging.DEBUG)
        logging.getLogger('coolisf.morph').setLevel(logging.DEBUG)
        logging.getLogger('coolisf.processors').setLevel(logging.DEBUG)


def print_dict(a_dict, rp, indent=0):
    indent_str = '  ' * (indent + 1)
    for k, v in a_dict.items():
        rp.write("{i}- {k}: ".format(i=indent_str, k=k))
        if isinstance(v, collections.Mapping):
            rp.print()
            print_dict(v, rp, indent + 1)
        else:
            rp.print(v)
    

def show_isf_info(cli, args):
    rp = TextReport()
    rp.header(f"coolisf - Python implementation of the Integrated Semantic Framework - Version {__version__}")
    config = read_config()  # make sure that the configuration file is created
    cfg_mgr = _get_config_manager()
    ghub = GrammarHub()
    config_loc = cfg_mgr.locate_config()
    ace_path = ghub.to_path(config['ace'])
    # report it
    rp.print("Configuration file: {}".format(config_loc))
    rp.print("Data folder: {}".format(config['data_root']))
    rp.print("ACE path: {}".format(ace_path))
    if args.detail:
        print_dict(config, rp)


# app instance
app = CLIApp(f"coolisf - Integrated Semantic Framework - Version {__version__}", logger=__name__, config_logging=isf_config_logging)


def make_task(name, func):
    ''' Add standard ISF options to a cli task '''
    task = app.add_task(name, func=func)
    task.add_argument('-o', '--output', help='Output file')
    task.add_argument('-g', '--grammar', help="Grammar name", default="ERG_ISF")
    task.add_argument('--wsd', help='Word Sense Disambiguator', default=ttl.Tag.LELESK)
    task.add_argument('-f', '--format', help='Output format', choices=OUTPUT_FORMATS, default=OUTPUT_DMRS)
    task.add_argument('--nocache', help='Do not cache parse result', action='store_true', default=None)
    task.add_argument('-n', '--topk', help="Limit number of parses returned by ACE", type=int, default=None)
    task.add_argument('-m', '--max', help="Only process top m items", default=None, type=int)
    task.add_argument('-c', '--compact', help="Produce compact outputs", action="store_true")
    task.add_argument('--nodmrs', help="Do not generate DMRS XML", action="store_true")
    task.add_argument('--shallow', help="With shallow", action="store_true")
    return task


def main():
    task = make_task('parse', func=parse_isf)
    task.add_argument('infile', help='Path to input text file')

    task = make_task('text', func=parse_text)
    task.add_argument('input', help='Any text')

    # batch processing a raw text corpus
    task = make_task('bib', func=parse_bib)
    task.add_argument('input', help='Path to raw biblioteca')
    # Create ISF gold profile
    task = app.add_task('gold', lambda cli, args: generate_gold_profile(), help='Extract gold profile')

    # Extract sentences from TSDB profile
    task = make_task('tsdb', func=extract_tsdb)
    task.add_argument('path', help='Path to TSDB profile folder or XML doc')
    task.add_argument('--ttl', help='Path to TTL files')
    task.add_argument('--name', help='Document canonical name')
    task.add_argument('--title', help='Document title')
    task.add_argument('--isf', help="Perform ISF transformation", action="store_true")
    task.add_argument('--ident', nargs='*')
    task.add_argument('--ids', nargs='*')

    # re-tag a document
    task = make_task('tag', func=retag_doc)
    task.add_argument('path', help='Path to document file (xml or xml.gz)')
    task.add_argument('--ttl', help='Path to TTL files')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])
    task.add_argument('--nogold', help='Do not tag DMRS with gold TTL, import TTL as shallow only', action='store_true')
    task.add_argument('-y', '--yes', help='Answer yes to everything', action='store_true')
    task.add_argument('--on_error', help='What to do when error occurred', choices=['remove', 'ignore', 'raise'], default='raise')
    task.add_argument('--mode', help='SensePred predicate choosing mode', choices=Lexsem.MODES)
    task.add_argument('--ident', nargs='*')
    task.add_argument('--forgive', help='Do not halt on error', action='store_true')

    # ISF to TTL
    task = make_task('ttl', func=export_ttl)
    task.add_argument('path', help='Path to XML doc')
    task.add_argument('--with-lemmas', help='Add lemmas to sentences', action="store_true")
    task.add_argument('-e', '--emptyfile', help='Output empty sentences list')
    task.add_argument('--ttl_format', help='TTL format', default=ttl.MODE_TSV, choices=[ttl.MODE_JSON, ttl.MODE_TSV])

    # Export to visko
    task = app.add_task('export', func=to_visko)
    task.add_argument('-f', '--file', help='MRS file')
    task.add_argument('biblioteca')
    task.add_argument('corpus')
    task.add_argument('doc')
    task.add_argument('-k', '--topk', help='Only extract top K sentences')
    task.add_argument('-b', '--bibloc', help='Path to Biblioteche folder (corpus collection root)')
    task.add_argument('--separate', help='One file for each sentence', action='store_true')
    task.add_argument('--top1dmrs', help='When ACE\'s option -1Tf is used', action='store_true')
    task.add_argument('--forgive', help='Do not halt on error', action='store_true')

    # show ISF configuration
    task = app.add_task('info', func=show_isf_info)
    task.add_argument('--detail', help='Show detailed configuration', action='store_true')
    app.run()


if __name__ == "__main__":
    main()
