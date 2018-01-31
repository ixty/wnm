#!/usr/bin/env python
# coding: utf-8
import sys, os, json, csv, gzip
from wnm_utils import *

# submarine cable database
url         = 'http://download.maxmind.com/download/worldcities/worldcitiespop.txt.gz'
path_raw    = './data-raw/worldcitiespop.txt.gz'
path_out    = './data/cities.json'

def geo_download():
    print '=' * 40
    print '> updating world cities database'
    print '=' * 40
    if not get_url(url, path_raw, chunk_size=2048):
        return -1

    print '> done'
    return 0

def geo_rebuild():

    geo = {}
    n = 0

    print '> processing %s' % path_raw
    with gzip.open(path_raw, 'rb') as f:
        rd = csv.reader(f, delimiter=',')
        hdr = rd.next()
        for row in rd:
            cc      = row[0].upper()
            ct      = row[1].decode('latin-1')
            ct      = ct.lower().replace(' ', '-').encode('utf-8')
            city    = row[2].decode('latin-1')
            city    = city.lower().replace(' ', '-').encode('utf-8')
            state   = row[3]
            pop     = int(row[4]) if len(row[4]) else 0
            lat     = float(row[5])
            lng     = float(row[6])

            if not cc in geo:
                geo[cc] = {}

            # include state in cityname for the us
            if cc == 'US':
                city = '%s-%s' % (state, city)
                ct = '%s-%s' % (state, ct)

            # update if city is not known yet, or if its a city with same name but more population
            if not city in geo[cc] or pop > geo[cc][city]['pop']:
                geo[cc][city] = {'lat': lat, 'lng': lng, 'pop': pop }
                if ct != city:
                    geo[cc][ct] = {'lat': lat, 'lng': lng, 'pop': pop }
            # else: pass

            n += 1

    geo2 = {}
    for cc in geo:
        geo2[cc] = {}
        for city in geo[cc]:
            geo2[cc][city] = [ geo[cc][city]['lat'], geo[cc][city]['lng'] ]

    wnm_save(path_out, geo2)

    return 0


# =================================
# main
# =================================
def usage():
    print '%s usage <command>' % sys.argv[0]
    print ''
    print 'commands:'
    print '    download             -- download geo cities database'
    print '    rebuild              -- rebuild local json database'
    print '    update               -- download & rebuild'
    print
    sys.exit(1)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    action = sys.argv[1]

    if action == 'download':
        geo_download()

    elif action == 'update':
        if geo_download():
            sys.exit(-1)
        if geo_rebuild():
            sys.exit(-1)

    elif action == 'rebuild':
        if geo_rebuild():
            sys.exit(-1)

    else:
        print '[-] unknown command "%s"' % action
        sys.exit(-1)

    sys.exit(0)

