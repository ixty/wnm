#!/usr/bin/env python
# coding: utf-8
import os, sys, datetime, time, json, gc, ipaddress
from subprocess import Popen, PIPE
from wnm_utils  import *
from tqdm       import tqdm

# =================================
# vars
# =================================

# url for bgp data

# EU:   http://routeviews.org/route-views.linx/bgpdata/2015.01/RIBS/rib.20150105.0800.bz2
# NA:   http://routeviews.org/route-views.eqix/bgpdata/2017.11/RIBS/rib.20171113.1600.bz2
# PAC:  http://routeviews.org/route-views.sg/bgpdata/2017.11/RIBS/rib.20171112.1000.bz2
# AF:   http://routeviews.org/route-views.jinx/bgpdata/2017.11/RIBS/rib.20171112.2000.bz2
# SA:   http://routeviews.org/route-views.saopaulo/bgpdata/2017.11/RIBS/rib.20171113.0000.bz2

# we try to get 1 bgp view from each continent
bgp_provs = [ 'linx', 'eqix', 'jinx', 'saopaulo', 'sg' ]

url_bgp             = 'http://routeviews.org/route-views.%s/bgpdata/%s/RIBS/rib.%s.0000.bz2'
path_bin_bgpdump    = './bins/bgpdump'
path_bgp_dir        = './data-raw/'
path_bgp_bz2        = path_bgp_dir  + 'bgp-%s.bz2'
path_bgp_bz2_bak    = path_bgp_dir  + 'bgp-%s.bak.bz2'
path_bgp_db         = './data/bgp.json'

# =================================
# funcs
# =================================
def bgp_download(ix):
    path = path_bgp_bz2 % ix
    pbak = path_bgp_bz2_bak % ix

    # backup current bgp db if any
    if os.path.exists(path):
        if os.path.exists(pbak):
            os.unlink(pbak)
        os.rename(path, pbak)

    # try to download today's db
    d = datetime.date.today()
    url = url_bgp % (ix, d.strftime('%Y.%m'), d.strftime('%Y%m%d'))
    if not get_url(url, path):
        # try yesterday's db
        d = datetime.date.today() - datetime.timedelta(days=1)
        url = url_bgp % (ix, d.strftime('%Y.%m'), d.strftime('%Y%m%d'))
        if not get_url(url, path):
            return -1

    print '> downloaded [%s] bgp database.' % ix
    return 0

def bgp_download_all():
    print '=' * 40
    print '> updating BGP database'
    print '=' * 40
    ret = 0
    for ix in bgp_provs:
        if bgp_download(ix):
            print '> failed to download [%s] bgp database.' % ix
            ret -= 1
    print '> done %d/%d' % (len(bgp_provs) + ret, len(bgp_provs))
    return ret

def bgp_load(path):
    pop = Popen([path_bin_bgpdump, '-m', path], stdout=PIPE, stderr=PIPE)
    data = pop.stdout.read()
    try:
        pop.kill()
    except:
        pass
    return data

def bgp_build(asl, ix):
    path = path_bgp_bz2 % ix

    print '> loading %s' % path
    data = bgp_load(path)
    lines = data.splitlines()

    # free memory
    data = ''
    gc.collect()

    print '> processing %s' % path
    for l in tqdm(lines):
        if not len(l):
            break
        tmp = ascii_clean(l).split('|')
        if len(tmp) < 7:
            print '! %s ' % l
            continue
        pfx     = tmp[5]
        cstr    = tmp[6].replace('{', '').replace('}', '').replace(',', ' ')
        chain   = [ int(_) for _ in cstr.split(' ') ]
        asn     = chain[-1]
        # print 'cidr[%s] chain[%r] as[%d]' % (pfx, chain, asn)

        for i in range(len(chain)-1):
            asn_link(asl, chain[i], chain[i+1])

        # skip private prefixes
        p = ipaddress.ip_network(unicode(pfx), strict=0)
        if p.is_multicast or p.is_private or p.is_unspecified or p.is_reserved or p.is_loopback or p.is_link_local:
            continue

        # add prefix to AS
        aso = asn_check(asl, asn)
        if pfx not in aso['prefix']:
            aso['prefix'].append(pfx)
            if ':' in pfx:
                aso['prefix6'] += 1
            else:
                aso['prefix4'] += 1

    # free memory
    lines = []
    gc.collect()
    return 0

def bgp_build_all():
    asl = {}

    # build all bgp route views
    for ix in bgp_provs:
    # for ix in ['jinx']:
        bgp_build(asl, ix)

    # dump output db
    wnm_save(path_bgp_db, asl)

    return 0

# =========================================================================== #
# utils
# =========================================================================== #
def ascii_clean(s):
    return filter(lambda x: x in string.printable, s)

def asn_check(asl, asn):
    if not asn in asl:
        asl[asn]                = {}
        asl[asn]['asn']         = asn
        asl[asn]['prefix']      = []
        asl[asn]['prefix4']     = 0
        asl[asn]['prefix6']     = 0
        asl[asn]['links']       = []
    return asl[asn]

def asn_link(asl, asn1, asn2):
    as1 = asn_check(asl, asn1)
    as2 = asn_check(asl, asn2)

    if asn1 not in as2['links']:
        as2['links'].append(asn1)
    if asn2 not in as1['links']:
        as1['links'].append(asn2)


# =================================
# main
# =================================
if __name__ == '__main__':
    if not os.path.exists(path_bgp_dir):
        os.mkdir(path_bgp_dir)

    if len(sys.argv) < 2:
        print 'usage: %s [update|download|rebuild|test]' % sys.argv[0]
        sys.exit(-1)

    action = sys.argv[1]
    if action == 'update':
        if bgp_download_all():
            print '[-] error downloading bgp view'
            sys.exit(-1)
        if bgp_build_all():
            print '[-] error building bgp db'
            sys.exit(-1)

    elif action == 'download':
        if bgp_download_all():
            print '[-] error downloading bgp view'
            sys.exit(-1)

    elif action == 'rebuild':
        if bgp_build_all():
            print '[-] error building bgp db'
            sys.exit(-1)

    elif action == 'test':

        print '> loading db..'
        with open(path_bgp_db, 'rb') as f:
            db = json.load(f)
        print json.dumps(db['21502'], indent=4, sort_keys=1)

    else:
        print '[-] unknown command "%s"' % action
        print 'usage: %s [update|download|rebuild|test]' % sys.argv[0]
        sys.exit(-1)

    sys.exit(0)
