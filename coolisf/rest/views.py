#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
coolisf REST API for Django site
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import json
import logging
import django
from django.http import HttpResponse, Http404

from texttaglib.chirptext import ttl
import coolisf
from coolisf import GrammarHub
from coolisf.model import Reading

# ---------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------

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
    logging.getLogger(__name__).info("Parsing sentence: ... " + sentence_text)
    sent = ghub.parse_json(sentence_text, grammar, parse_count, tagger)
    logging.getLogger(__name__).debug("Shallow: {}".format(sent['shallow']))
    logging.getLogger(__name__).debug("Parses: {}".format(len(sent)))
    logging.getLogger(__name__).info("Done parsing")
    return sent


@jsonp
def version(request):
    return {'product': 'djangoisf',
            'server': 'coolisf-{}/Django-{}'.format(coolisf.__version__, django.get_version())}
