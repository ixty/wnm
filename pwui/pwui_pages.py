#!/usr/bin/env python
# coding: utf-8
import math
import pwui_jinja
from   pwui_tools import *


# =========================================================================== #
# build data for country world rankings
# =========================================================================== #
cn_ranks = {
    'world':    [ 'World Internet Map', 'AS',               ''],
    'nets_loc': [ 'Networks (AS)',      'AS',               'Autonomous Systems repartition around the world'           ],
    'nets_ext': [ 'Incoming Networks',  'ext AS',           'External AS connected to countries, aka country "open-ness" to the rest of the world'   ],
    'num_fac':  [ 'Facilities',         'facilities',       'Private & public internet points of peering'               ],
    'num_ix':   [ 'Exchanges (IX)',     'IX',               'Public internet points of peering'                         ],
    'landings': [ 'Landings',           'landings',         'Submarine cables landings'                                 ],
    'addr4':    [ 'IPv4 Addresses',     'IPv4 addresses',   'IPv4 addresses repartition around the world'               ],
    'addr6':    [ 'IPv6 Addresses',     'IPv6 addresses',   'IPv6 addresses repartition around the world'               ],
}

def pagedata_rank(db, key, opt):
    # get options for this view
    r = cn_ranks[key]

    # create default empty page struct
    p = page_default('ranks' if key != 'world' else 'world')
    p['title'] = r[0]
    p['text' ] = r[2]
    p['key'  ] = key
    p['opt']   = opt
    p['unit']  = r[1]
    unit       = r[1]

    # build data list for each countrie's colorization
    for cc in db['countries']:
        if key == 'world':
            n = len(db['countries'][cc]['nets_loc'])
        elif isinstance(db['countries'][cc][key], list):
            n = len(db['countries'][cc][key])
        else:
            n = db['countries'][cc][key]

        if len(opt):
            if db['countries'][cc][opt]:
                if opt == 'pop':
                    div = float(db['countries'][cc][opt]) / 1000000.0
                    n /= div if div >= 1 else 1
                    unit = r[1] + ' per M inhabitant'
                    p['detail'] = ' per M inhabitant'
                elif opt == 'lnd':
                    div = float(db['countries'][cc][opt]) / 1000.0
                    n /= div if div >= 1 else 1
                    unit = r[1] + ' per 1,000 km^2'
                    p['detail'] = ' per 1,000 km^2'
            else:
                n = 0

        itm = {}
        itm['cc']   = db['countries'][cc]['cc']
        itm['iso3'] = db['countries'][cc]['iso3']
        itm['name'] = db['countries'][cc]['name']
        itm['val']  = n
        itm['col']  = max(1, math.log(n + 1))
        # itm['col']  = n
        itm['hover']= '%s %s' % (pwui_jinja.bignumb(n), unit)

        if n == 0:
            itm['col'] = 0.1
        p['data'].append(itm)

    # get max color val
    p['col_max']    = max([itm['col'] for itm in p['data']] + [1])
    p['total']      = sum([itm['val'] for itm in p['data']])

    # sort data
    p['data'] = sorted(p['data'], key=lambda n: n['val'], reverse=1)
    for i in range(len(p['data'])):
        p['data'][i]['hover'] = '# %d<br/>' % (i+1) + p['data'][i]['hover']


    # add facility bubbles
    if key == 'num_fac' or key == 'world':
        for i in db['facilities']:
            f = db['facilities'][i]
            if len(f['nets']) > 0:
                page_add_facility(p, f)

    # add facility bubbles - only those with ixs
    if key == 'num_ix':
        for i in db['facilities']:
            f = db['facilities'][i]
            if len(f['ix']) > 0:
                page_add_ix(p, f)

    # add landings bubbles
    if key == 'landings' or key == 'world':
        for i in db['landings']:
            page_add_landing(p, db['landings'][i])

    return p


# =========================================================================== #
# build data for country view
# =========================================================================== #
def pagedata_country(db, cc):
    p = page_default('country')
    country = db['countries'][cc]

    # get country incoming/outgoing connectivity score for each country
    nl_dir_inc = { cc: len(country['links_dir_inc'][cc][subcat]) for cc in country['links_dir_inc'] for subcat in country['links_dir_inc'][cc] }
    nl_dir_out = { cc: len(country['links_dir_out'][cc][subcat]) for cc in country['links_dir_out'] for subcat in country['links_dir_out'][cc] }
    nl_ind_inc = { cc: len(country['links_ind_inc'][cc][subcat]) for cc in country['links_ind_inc'] for subcat in country['links_ind_inc'][cc] }
    nl_ind_out = { cc: len(country['links_ind_out'][cc][subcat]) for cc in country['links_ind_out'] for subcat in country['links_ind_out'][cc] }

    # add all countries with links to this one
    for cc in country['links_dir_inc'].keys() + country['links_ind_inc'].keys():
        page_add_cnl(p, db['countries'][cc], nl_dir_inc.get(cc, 0), nl_ind_inc.get(cc, 0))

    # get max val
    p['col_max'] = max([itm['col'] for itm in p['data']] + [1])

    # add current currently selected country with max_val
    page_add_cn(p, country, p['col_max'], p['col_max'], 'Selected Country')

    # sort data
    p['data'] = sorted(p['data'], key=lambda n: len(n['val']) if isinstance(n['val'], list) else n['val'], reverse=1)

    # add arcs for outgoing links
    for cc in country['links_dir_out'].keys() + country['links_ind_out'].keys():
        if cc != '??':
            page_add_link_c2c(p, country, db['countries'][cc], nl_dir_out.get(cc, 0), nl_ind_out.get(cc, 0))

    # add facilities
    for fid in country['fac_ids']:
        f = db['facilities'][str(fid)]
        if len(f['nets']) > 0:
            page_add_facility(p, f)

    # add landings
    for lid in country['landings']:
        page_add_landing(p, db['landings'][lid])

    return p


# =========================================================================== #
# build data for network view
# =========================================================================== #
def pagedata_net(db, asn):
    p = page_default('net')
    net = db['nets'][asn]

    # get outgoing country links for this network
    nl_dir = { cc: len(net['links_dir'][cc][subcat]) for cc in net['links_dir'] for subcat in net['links_dir'][cc] }
    nl_ind = { cc: len(net['links_ind'][cc][subcat]) for cc in net['links_ind'] for subcat in net['links_ind'][cc] }

    for cc in nl_dir.keys() + nl_ind.keys():
        page_add_cnl(p, db['countries'][cc], nl_dir.get(cc, 0), nl_ind.get(cc, 0))

    p['col_max'] = max([itm['col'] for itm in p['data']] + [1])
    page_add_cn(p, db['countries'][net['cc']], p['col_max'], p['col_max'], 'Home Country')

    # sort data
    p['data'] = sorted(p['data'], key=lambda n: len(n['val']) if isinstance(n['val'], list) else n['val'], reverse=1)

    # add facilities
    for i in net['fac_ids']:
        page_add_facility(p, db['facilities'][str(i)])

    # add country links
    for cc in net['links_dir'].keys() + net['links_ind'].keys():
        if cc != '??':
            page_add_link_n2c(db, p, net, db['countries'][cc], nl_dir.get(cc, 0), nl_ind.get(cc, 0))

    return p


# =========================================================================== #
# build page data for facility
# =========================================================================== #
def pagedata_fac(db, fid):
    p = page_default('facility')
    f = db['facilities'][fid]

    scores = {}
    scores[f['country']] = 1
    for xid in f['ix']:
        ix = db['ixs'][str(xid)]
        if not ix['country'] in scores:
            scores[ix['country']] = 0
        scores[ix['country']] += 1

    for cc in scores:
        page_add_cn(p, db['countries'][cc], scores[cc], scores[cc], 'linked to %d exchanges in %s' % (scores[cc], cc))

    intpres = []
    for asn in f['nets']:
        net = db['nets'][str(asn)]
        if net['cc'] != f['country'] and net['cc'] != '??' and not net['cc'] in intpres:
            intpres += [ net['cc'] ]
    f['net_countries'] = intpres

    page_add_facility(p, f)

    p['col_max'] = max([itm['col'] for itm in p['data']] + [1])
    return p


# =========================================================================== #
# build page data for exchange
# =========================================================================== #
def pagedata_ix(db, xid):
    p = page_default('exchange')
    ix = db['ixs'][xid]

    scores = {}
    for fid in ix['facilities']:
        fac = db['facilities'][str(fid)]
        page_add_facility(p, fac)
        if not fac['country'] in scores:
            scores[fac['country']] = 0
        scores[fac['country']] += 1

    for cc in scores:
        page_add_cn(p, db['countries'][cc], scores[cc], scores[cc], '%d facilities in %s' % (scores[cc], cc))

    p['col_max'] = max([itm['col'] for itm in p['data']] + [1])
    return p


# =========================================================================== #
# build page data for cable
# =========================================================================== #
def pagedata_cable(db, cid):
    p = page_default('cable')
    cable = db['cables'][cid]

    scores = {}
    for lid in cable['landings']:
        ld = db['landings'][lid]
        page_add_landing(p, ld)
        if not ld['cc'] in scores:
            scores[ld['cc']] = 0

        scores[ld['cc']] += 1

    for cc in scores:
        page_add_cn(p, db['countries'][cc], scores[cc], scores[cc], '%d landings in %s' % (scores[cc], cc))


    p['col_max'] = max([itm['col'] for itm in p['data']] + [1])
    return p


# =========================================================================== #
# build page data for landing
# =========================================================================== #
def pagedata_landing(db, lid):
    p = page_default('landing')
    landing = db['landings'][lid]

    page_add_landing(p, landing)

    scores = {}
    for cid in landing['cables']:
        for lid in db['cables'][cid]['landings']:
            c = db['landings'][lid]['cc']
            if not c in scores:
                scores[c] = []
            scores[c] += [ db['cables'][cid]['name'] ]

    for cc in scores:
        if cc != landing['cc']:
            n = len(scores[cc])
            hov = '<b>Reachable by</b>'
            for s in scores[cc]:
                hov += '<br/>%s' % s
            page_add_cn(p, db['countries'][cc], n, n, hov)

    p['col_max'] = max([itm['col'] for itm in p['data']] + [1])
    page_add_cn(p, db['countries'][landing['cc']], p['col_max'] + 1, p['col_max'] + 1, 'Home country')
    p['col_max'] += 1

    return p

