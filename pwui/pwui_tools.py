#!/usr/bin/env python
# coding: utf-8
import os, math, ipaddress
from pwui_colors import pwui_colors

# returns % of non-available memory
def get_mem_usage():
    with os.popen('free -b') as p:
        for l in p.readlines():
            if l.lower()[0:3] != 'mem':
                continue
            tmp = l.split()
            tot = float(tmp[1])
            if len(tmp) >= 7:
                return (tot - float(tmp[6])) / tot * 100.0
            return float(tmp[2]) / tot * 100.0
        return -1

# =========================================================================== #
# ip lookup tools (ip to ASn)
# =========================================================================== #
cidr_lookup = {}    # key = cidr, val = asn
def _lookup_cidr_build(db):
    for asn in db['nets']:
        for pfx in db['nets'][asn]['prefix']:
            if not pfx in cidr_lookup:
                cidr_lookup[pfx] = []
            cidr_lookup[pfx].append(asn)

def lookup_cidr(db, ip_or_cidr, ipv6=0):
    if not len(cidr_lookup):
        _lookup_cidr_build(db)

    if '/' in ip_or_cidr:
        cidr_base = ip_or_cidr.split('/')[0]
        cidr_mask = int(ip_or_cidr.split('/')[1])
    else:
        cidr_base = ip_or_cidr
        cidr_mask = 128 if ipv6 else 32

    for i in range(cidr_mask, 0, -1):
        cidr = str(ipaddress.ip_network(u"%s/%d" % (cidr_base, i), strict=False))
        if cidr in cidr_lookup:
            return cidr_lookup[cidr]

    return []


# =========================================================================== #
# page data building tools
# =========================================================================== #

# ========================= #
# sizing for bubbles & arcs
# ========================= #
def size_facility(fac):
    n = len(fac['nets'])
    if not n:
        v = 0
    else:
        v = max(0, math.log(n, 2))
        v += 1

    return 2.5 * v + 1

def size_facility_ix(fac):
    return 5 * len(fac['ix'])

def size_arc(ldir, lind):
    v = math.log(100 * ldir + 5*lind + 1)
    if v < 1:
        v = 1
    return 1.5 * v

def size_landing(ld):
    return 2 * len(ld['cables']) + 4,

# create an empty page data
def page_default(pn=''):
    return { 'pagename': pn, 'total': 0, 'col_max': 0, 'data': [], 'bubbles': [], 'arcs': [] }

# ========================= #
# add bubbles
# ========================= #
def page_add_bubble(page, name, lat, lng, radius, fill, hover, href):
    page['bubbles'].append({
        'name':         name,
        'latitude':     lat,
        'longitude':    lng,
        'radius':       radius,
        'border':       1,
        'fillKey':      fill,
        'hover':        hover,
        'url':          href,
    })

def page_add_facility(page, f):
    lat = f['lat'] if f['citydist'] <= 10 else f['citycoords'][0]
    lng = f['lng'] if f['citydist'] <= 10 else f['citycoords'][1]
    hov = 'city: %s<br/>ix: %s<br/>nets: %s<br/>' % (f['city'], len(f['ix']), len(f['nets']))
    url = '/fac/%d' % f['id']
    page_add_bubble(page, f['name'], lat, lng, size_facility(f), 'facility', hov, url)

def page_add_ix(page, f):
    hov = 'city: %s<br/>ix: %s<br/>nets: %s<br/>' % (f['city'], len(f['ix']), len(f['nets']))
    url = '/fac/%d' % f['id']
    page_add_bubble(page, f['name'], f['lat'], f['lng'], size_facility_ix(f), 'facility', hov, url)

def page_add_landing(page, l):
    hov = 'cables: %d<br/>' % len(l['cables'])
    url = '/landing/%s' % l['id']
    page_add_bubble(page, l['name'], l['lat'], l['lng'], size_landing(l), 'landing', hov, url)


# ========================= #
# add arcs
# ========================= #
def page_add_arc(page, org, dst, name, hov, size, color, cclass):
    page['arcs'].append({
        'origin': {
            'latitude':     org[0],
            'longitude':    org[1],
        },
        'destination': {
            'latitude':     dst[0],
            'longitude':    dst[1],
        },
        'name':             name,
        'hover':            hov,
        'orig_width':       size,
        'orig_color':       color,
        'cclass':           cclass,
        'options': {
            'strokeWidth':  size,
            'strokeColor':  color,
        }
    })

def page_add_link_c2c(page, c1, c2, ldir, lind):
    name    = '%s to %s' % (c1['cc'], c2['cc'])
    hover   = 'Direct Outgoing Links: %d<br/>Indirect Outgoing Links: %d' % (ldir, lind)
    size    = size_arc(ldir, lind)
    color   = pwui_colors['link1'] if ldir > 0 else pwui_colors['link2']
    cclass  = 'dirlink' if ldir > 0 else 'indlink'
    page_add_arc(page, c1['center'], c2['center'], name, hover, size, color, cclass)

def page_add_link_n2c(db, page, net, c, ldir, lind):
    name    = '%s to %s' % (net['name'], c['name'])
    hover   = 'Direct Links: %d<br/>Indirect Links: %d' % (ldir, lind)
    size    = size_arc(ldir, lind)
    color   = pwui_colors['link1'] if ldir > 0 else pwui_colors['link2']
    cclass  = 'dirlink' if ldir > 0 else 'indlink'
    page_add_arc(page, db['countries'][net['cc']]['center'], c['center'], name, hover, size, color, cclass)


# ========================= #
# add country colors
# ========================= #
def page_add_cn(page, cn, val, col, hover):
    page['data'].append({
        'cc':   cn['cc'],
        'iso3': cn['iso3'],
        'name': cn['name'],
        'val':  val,
        'col':  col,
        'hover': hover,
    })

def page_add_cnl(page, cn, ld, li):
    hov = 'Direct Links: %d<br/>Indirect Links: %d' % (ld, li)
    val = 10 * ld + li
    page_add_cn(page, cn, val, val, hov)

