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

from chirptext import texttaglib as ttl
import coolisf
from coolisf import GrammarHub
from coolisf.model import Reading

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
RESULTS = (1, 5, 10, 20, 30, 40, 50, 100, 500)
TAGGERS = {ttl.Tag.LELESK: "LeLesk", ttl.Tag.MFS: "MFS", ttl.Tag.DEFAULT: "None"}
ghub = GrammarHub()


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


@jsonp
def generate(request):
    grammar = request.POST.get('grammar', '')
    # parse_count = request.GET['parse_count']
    mrs = request.POST.get('mrs', '')
    print("Grammar: {}".format(grammar))
    print("MRS: {}".format(mrs))
    if grammar not in ghub.names:
        raise Http404('Unknown grammar')
    sents = [s.text for s in ghub[grammar].generate(Reading(mrs))]
    print("Generated: {}".format(sents))
    return sents


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
    elif int(parse_count) < 0:
        raise Http404('Invalid parse count: ' + parse_count)
    elif tagger not in TAGGERS:
        raise Http404('Unknown tagger: ' + tagger)
    elif grammar not in ghub.names:
        raise Http404('Unknown grammar')

    # Parse sentence
    logger.info("Parsing sentence: ... " + sentence_text)
    sent = ghub.parse_json(sentence_text, grammar, parse_count, tagger)
    logger.debug("Shallow: {}".format(sent['shallow']))
    logger.debug("Parses: {}".format(len(sent)))
    logger.info("Done parsing")
    return sent


@jsonp
def version(request):
    return {'product': 'djangoisf',
            'version': __version__,
            'server': 'coolisf-{}/Django-{}'.format(coolisf.__version__, django.get_version())}
