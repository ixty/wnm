#!/usr/bin/env python
# coding: utf-8
import jinja2

# =========================================================================== #
# jinja filters
# =========================================================================== #

# custom filter
def bandwith(mbits):
    if mbits >= 1000 * 1000:
        return '%.1f Tbps' % (float(mbits) / 1000000.0)
    elif mbits >= 1000:
        return '%.1f Gbps' % (float(mbits) / 1000.0)
    return '%d Mbps' % mbits

def bandwith2(mbits):
    if mbits >= 1000 * 1000:
        return '%.0f Tbps' % (float(mbits) / 1000000.0)
    elif mbits >= 1000:
        return '%.0f Gbps' % (float(mbits) / 1000.0)
    return '%d Mbps' % mbits

def bignumb(val):
    val = long(float(val))
    if   val >= 1000*1000*1000*1000*1000:
        return '%.1e' % val
    elif val >= 1000*1000*1000*1000:
        return '%.1f T' % (float(val) / (1000*1000*1000*1000))
    elif val >= 1000*1000*1000:
        return '%.1f B' % (float(val) / (1000*1000*1000))
    elif val >= 1000*1000:
        return '%.1f M' % (float(val) / (1000*1000))
    elif val >= 1000:
        return '%.1f k' % (float(val) / 1000)
    elif val != 0:
        return '%d' % val
    else:
        return '0'

def distance(val):
    if val < 0:
        return '?'
    return "{:,} km".format(val)

def spaceless(s):
    out = []
    for l in s.splitlines():
        l = l.strip()
        if not len(l):
            continue
        out += [l]
    return ''.join(out)

def stripblock(s):
    out = []
    for l in s.splitlines():
        l = l.strip()
        if not len(l):
            continue
        out += [l]
    return '\n'.join(out)

jinja2.filters.FILTERS['bandwith']      = bandwith
jinja2.filters.FILTERS['bandwith2']     = bandwith2
jinja2.filters.FILTERS['spaceless']     = spaceless
jinja2.filters.FILTERS['stripblock']    = stripblock
jinja2.filters.FILTERS['bignumb']       = bignumb
jinja2.filters.FILTERS['distance']      = distance
