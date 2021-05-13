# -*- coding: utf-8 -*-

"""
Raw Text Corpus manager
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import os
import json

from texttaglib.chirptext import FileHelper
from texttaglib.chirptext.chio import CSV


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

class MetaObject(object):

    def __init__(self, path):
        self.__path = FileHelper.abspath(path)
        self.__metadata = {}

    @property
    def path(self):
        return self.__path

    def folder_meta_path(self):
        return os.path.join(self.path, 'isf.metadata.json')

    def file_meta_path(self):
        return self.path + '.isf.metadata.json'

    @property
    def metadata(self):
        if not self.__metadata:
            if os.path.isfile(self.path):
                meta_path = self.file_meta_path()
            elif os.path.isdir(self.path):
                meta_path = self.folder_meta_path()
            else:
                raise Exception("Invalid path {}".format(self.path))
            # if meta file exists, read it
            if os.path.isfile(meta_path):
                with open(meta_path, encoding='utf-8') as metafile:
                    metadata = json.load(metafile)
                    if metadata:
                        self.__metadata = metadata
        return self.__metadata

    def getinfo(self, metadata_key, default=None):
        if metadata_key in self.metadata:
            return self.metadata[metadata_key]
        else:
            return default

    def write_folder_meta(self, metadata):
        with open(self.folder_meta_path(), 'w', encoding='utf-8') as outfile:
            metadata_string = json.dumps(metadata, ensure_ascii=False, indent=2)
            outfile.write(metadata_string)

    def write_file_meta(self, metadata):
        with open(self.file_meta_path(), 'w', encoding='utf-8') as outfile:
            metadata_string = json.dumps(metadata, ensure_ascii=False, indent=2)
            outfile.write(metadata_string)


class RawCollection(MetaObject):

    def __init__(self, path, name='', title='', *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.name = name if name else self.getinfo('name', os.path.basename(self.path))
        self.title = title if title else self.getinfo('title', '')

    def get_corpuses(self):
        corpuses = RawCorpusCollection()
        corpus_names = self.getinfo('corpuses', FileHelper.get_child_folders(self.path))
        for corpus_name in corpus_names:
            corpus_path = os.path.join(self.path, corpus_name)
            corpuses.add(RawCorpus(corpus_path))
        return corpuses

    def write_meta(self, name, title, corpuses):
        self.write_folder_meta({'name': name, 'title': title, 'corpuses': corpuses})


class RawCorpusCollection():
    def __init__(self, corpuses=None):
        self.__corpuses = list(corpuses) if corpuses else []
        self.__corpus_map = {c.name: c for c in self.__corpuses}

    def add(self, corpus):
        self.__corpuses.append(corpus)
        self.__corpus_map[corpus.name] = corpus

    def __iter__(self):
        return iter(self.__corpuses)

    def __len__(self):
        return len(self.__corpuses)

    def __getitem__(self, key):
        return self.__corpus_map[key]

    def __contains__(self, key):
        return key in self.__corpus_map


class RawCorpus(MetaObject):

    def __init__(self, path, name='', title='', *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.name = name if name else self.getinfo('name', os.path.basename(self.path))
        self.title = title if title else self.getinfo('title', '')
        self.format = self.getinfo('format', RawDocument.TXT_FORMAT)

    def get_documents(self):
        docs = []
        docnames = self.getinfo('documents', FileHelper.get_child_files(self.path))
        for docname in docnames:
            docs.append(RawDocument(os.path.join(self.path, docname), format=self.format))
        return docs

    def write_meta(self, name, title, documents, format='tsv'):
        self.write_folder_meta({'name': name, 'title': title, 'documents': documents, 'format': format})


class RawDocument(MetaObject):

    TXT_FORMAT = 'txt'
    TSV_FORMAT = 'tsv'

    def __init__(self, path, name='', title='', format=TXT_FORMAT, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self.name = name if name else self.getinfo('name', FileHelper.getfilename(self.path))
        self.title = title if title else self.getinfo('title', '')
        if format:
            self.format = format
        else:
            self.format = self.getinfo('format', RawDocument.TXT_FORMAT)

    def read_sentences(self):
        if self.format == RawDocument.TXT_FORMAT:
            sents = enumerate(FileHelper.read(self.path).splitlines())
        elif self.format == RawDocument.TSV_FORMAT:
            sents = CSV.read_tsv(self.path)
        return (RawSentence(ident, text) for ident, text in sents)


class RawDocumentCollection():
    def __init__(self, documents=None):
        self.__docs = list(documents) if documents else []
        self.__doc_map = {c.name: c for c in documents}

    def add(self, document):
        self.__docs.append(document)
        self.__doc_map[document.name] = document

    def __iter__(self):
        return iter(self.__docs)

    def __len__(self):
        return len(self.__docs)

    def __getitem__(self, key):
        return self.__doc_map[key]

    def __contains__(self, key):
        return key in self.__doc_map


class RawSentence(object):

    def __init__(self, ident, text):
        self.ident = ident
        self.text = text

    def __str__(self):
        return "[{}] {}".format(self.ident, self.text)
