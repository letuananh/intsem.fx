#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
YAWOL-Django - Yet Another Wordnet Online (REST server) for Django
Latest version can be found at https://github.com/letuananh/yawlib

References:
    Python documentation:
        https://docs.python.org/
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
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
__copyright__ = "Copyright 2017, yawlib"
__credits__ = []
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import json
import logging
import django
from django.http import HttpResponse, Http404

from chirptext.texttaglib import TagInfo
import coolisf
from coolisf.util import Grammar


# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# VIEWS
# ---------------------------------------------------------------------

def jsonp(func):
    ''' JSON/JSONP decorator '''
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        # ignore HttpResponse
        if isinstance(objects, HttpResponse):
            return objects
        # JSON/JSONP response
        data = json.dumps(objects)
        if 'callback' in request.GET:
            callback = request.GET['callback']
        elif 'callback' in request.POST:
            callback = request.POST['callback']
        else:
            return HttpResponse(data, "application/json")
        # is JSONP
        # logging.debug("A jsonp response")
        data = '{c}({d});'.format(c=callback, d=data)
        return HttpResponse(data, "application/javascript")
    return decorator


def index(request):
    return HttpResponse('coolisf-REST is up and running - coolisf-{v}/Django-{dv}'.format(v=coolisf.__version__, dv=django.get_version()), 'text/html')


RESULTS = (1, 5, 10, 20, 30, 40, 50, 100, 500)
TAGGERS = (TagInfo.LELESK, TagInfo.MFS)
GRAMMARS = ('ERG', 'JACY')  # TODO: Make this more flexible


@jsonp
def parse(request):
    ''' Parse a sentence using ISF
    Mapping: /restisf/parse/ '''
    # inputs
    sentence_text = request.GET['sent']
    parse_count = request.GET['parse_count']
    tagger = request.GET['tagger']
    grammar = request.GET['grammar']

    # validation
    if not sentence_text:
        raise Http404('Sentence cannot be empty')
    elif int(parse_count) not in RESULTS:
        raise Http404('Invalid parse count: ' + parse_count)
    elif tagger not in TAGGERS:
        raise Http404('Unknown tagger: ' + tagger)
    elif grammar not in GRAMMARS:
        raise Http404('Unknown grammar')

    # Parse sentence
    logger.info("Parsing sentence: " + sentence_text)
    sent = Grammar().parse(sentence_text, parse_count=parse_count)
    sent.tag(method=TagInfo.LELESK)

    # Return result
    return {'sent': sentence_text,
            'parse_count': parse_count,
            'tagger': tagger,
            'grammar': grammar,
            'parses': [x.dmrs().json() for x in sent]}


@jsonp
def mockup(request):
    ''' Parse a sentence using ISF
    Mapping: /restisf/parse/ '''
    sent = request.GET['sent']
    parse_count = request.GET['parse_count']
    tagger = request.GET['tagger']
    grammar = request.GET['grammar']
    mockup = {"lnk": {"from": -1, "to": -1}, "nodes": [{"type": "realpred", "senses": [{"lemma": "some", "type": "lelesk", "synsetid": "02267308-a"}], "lnk": {"from": 0, "to": 4}, "predicate": "_some_q", "pos": "q", "nodeid": 10000}, {"sortinfo": {"cvarsort": "x", "ind": "+", "num": "pl", "pers": "3"}, "senses": [{"lemma": "dog", "type": "lelesk", "synsetid": "02084071-n"}], "type": "realpred", "lnk": {"from": 5, "to": 9}, "predicate": "_dog_n_1", "pos": "n", "nodeid": 10001}, {"sortinfo": {"cvarsort": "e", "tense": "past", "mood": "indicative", "prog": "-", "sf": "prop", "perf": "-"}, "senses": [{"lemma": "bark", "type": "lelesk", "synsetid": "07376731-n"}], "type": "realpred", "lnk": {"from": 10, "to": 17}, "predicate": "_bark_v_1", "pos": "v", "nodeid": 10002}], "text": "Some dogs barked.", "links": [{"post": "H", "from": 0, "rargname": None, "to": 10002}, {"post": "H", "from": 10000, "rargname": "RSTR", "to": 10001}, {"post": "NEQ", "from": 10002, "rargname": "ARG1", "to": 10001}]}
    mockup2 = {"lnk": {"from": -1, "to": -1}, "nodes": [{"type": "realpred", "senses": [{"lemma": "some", "type": "lelesk", "synsetid": "02267308-a"}], "lnk": {"from": 0, "to": 4}, "predicate": "_some_q", "pos": "q", "nodeid": 10000}, {"sortinfo": {"cvarsort": "x", "ind": "+", "num": "pl", "pers": "3"}, "senses": [{"lemma": "dog", "type": "lelesk", "synsetid": "09886220-n"}], "type": "realpred", "lnk": {"from": 5, "to": 9}, "predicate": "_dog_n_1", "pos": "n", "nodeid": 10001}, {"sortinfo": {"cvarsort": "e", "tense": "past", "mood": "indicative", "prog": "-", "sf": "prop", "perf": "-"}, "senses": [{"lemma": "bark", "type": "lelesk", "synsetid": "07376731-n"}], "type": "realpred", "lnk": {"from": 10, "to": 17}, "predicate": "_bark_v_1", "pos": "v", "nodeid": 10002}], "text": "Some dogs barked.", "links": [{"post": "H", "from": 0, "rargname": None, "to": 10002}, {"post": "H", "from": 10000, "rargname": "RSTR", "to": 10001}, {"post": "NEQ", "from": 10002, "rargname": "ARG1", "to": 10001}]}

    if not sent:
        raise Http404('Invalid sentence')
    return {'sent': sent,
            'parse_count': parse_count,
            'tagger': tagger,
            'grammar': grammar,
            'parses': [mockup, mockup2]}


@jsonp
def version(request):
    return {'product': 'djangoisf',
            'version': __version__,
            'server': 'coolisf-{}/Django-{}'.format(coolisf.__version__, django.get_version())}
