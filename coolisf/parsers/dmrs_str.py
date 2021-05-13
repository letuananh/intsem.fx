# -*- coding: utf-8 -*-

"""
DMRS parser
"""

# This code is a part of coolisf library: https://github.com/letuananh/intsem.fx
# :copyright: (c) 2014 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: MIT, see LICENSE for more details.

import logging
from delphin.mrs import simplemrs


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------------------


DMRS_SIG = 'dmrs'
LIST_OPEN = '['
LIST_CLOSE = ']'
GROUP_OPEN = '{'
GROUP_CLOSE = '}'
ITEM_SEP = ';'
CFROM = '<'
FROMTOSEP = ':'
CTO = '>'
LINK_SIG = ':'
CARG_OPEN = '('
CARG_CLOSE = ')'


def tokenize_dmrs_str(dmrs_str):
    return simplemrs.tokenize(dmrs_str)


def parse_dmrs_str(dmrs_str):
    tokens = tokenize_dmrs_str(dmrs_str)
    return parse_dmrs(tokens)


def parse_dmrs(tokens):
    dmrs = {'nodes': [], 'links': []}
    expect(tokens, DMRS_SIG)
    expect(tokens, GROUP_OPEN)
    while len(tokens) > 2:
        nodeid = tokens.popleft()
        next_token = tokens.popleft()
        if next_token == LIST_OPEN:
            node = parse_node(nodeid, tokens)
            dmrs['nodes'].append(node)
        elif next_token == LINK_SIG:
            link = parse_link(nodeid, tokens)
            dmrs['links'].append(link)
        else:
            print("Cannot process {} from {}".format(next_token, tokens))
            break
        # next_token = tokens.popleft()
        # if next not in (ITEM_SEP, GROUP_CLOSE):
        #    raise Exception("Junk tokens at the end {}", next_token, tokens)
    if len(tokens) > 0:
        expect(tokens, GROUP_CLOSE)
    return dmrs


def expect(tokens, expected, message=None):
    actual = tokens.popleft()
    if actual != expected:
        if message:
            raise Exception(message)
        else:
            raise Exception("Expected {}, actual {}".format(expected, actual))
    else:
        return actual


def parse_node(nodeid, tokens):
    pred = tokens.popleft()
    expect(tokens, CFROM)
    cfrom = tokens.popleft()
    expect(tokens, FROMTOSEP)
    cto = tokens.popleft()
    expect(tokens, CTO)
    node = {'predicate': pred, 'nodeid': int(nodeid), 'lnk': {'from': int(cfrom), 'to': int(cto)}}
    if tokens[0] == CARG_OPEN:
        tokens.popleft()
        carg = tokens.popleft()
        if carg.startswith('"'):
            carg = carg[1:]
        if carg.endswith('"'):
            carg = carg[:-1]
        node['carg'] = carg
        expect(tokens, CARG_CLOSE)
    if tokens[0] != LIST_CLOSE and tokens[0] in 'xeiu':
        # next one should be cvarsort
        node['sortinfo'] = {'cvarsort': tokens.popleft()}
    while tokens[0] != LIST_CLOSE:
        # parse sortinfo
        token = tokens.popleft()
        k, v = token.rsplit('=', 1)
        # if k.lower() == 'carg':
        #     # add carg to sortinfo
        #     node['carg'] = v
        if k.startswith('synset'):
            if 'sense' not in node:
                node['sense'] = {}
            if k == 'synsetid':
                node['sense'][k] = v
            else:
                node['sense'][k[7:]] = v
        else:
            # add to sortinfo
            node['sortinfo'][k.lower()] = v
        pass
    expect(tokens, LIST_CLOSE)
    # take care of the last ;
    if tokens[0] == ITEM_SEP:
        tokens.popleft()
    return node


def parse_link(from_nodeid, tokens):
    rargname, post = tokens.popleft().split('/')
    expect(tokens, '-')
    expect(tokens, '>')
    to_nodeid = tokens.popleft()
    if to_nodeid.endswith(ITEM_SEP):
        to_nodeid = to_nodeid[:-1]
    elif tokens[0] == ITEM_SEP:
        tokens.popleft()
    return {'from': int(from_nodeid), 'to': int(to_nodeid), 'rargname': rargname, 'post': post}
