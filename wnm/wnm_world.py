#!/usr/bin/env python
# coding: utf-8
import sys, os, json, csv, zipfile
from wnm_utils import *

url = 'http://download.geonames.org/export/dump/countryInfo.txt'

path_raw    = './data-raw/worldinfo.txt'
path_out    = './data/worldinfo.json'

def download():
    print '=' * 40
    print '> updating country database'
    print '=' * 40

    if not get_url(url, path_raw, chunk_size=2048):
        return -1

    return 0

def rebuild():
    data = {}

    with open(path_raw, 'rb') as f:
        text = f.read()

    for l in text.splitlines():
        if l[0] == '#':
            hdr = l[1:]
            continue

        c = dict(zip(hdr.split('\t'), l.split('\t')))
        data[c['ISO']] = c

    wnm_save(path_out, data)

    return 0


# =================================
# main
# =================================
def usage():
    print '%s usage <command>' % sys.argv[0]
    print ''
    print 'commands:'
    print '    download             -- download world info databases'
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
        download()

    elif action == 'update':
        if download():
            sys.exit(-1)
        if rebuild():
            sys.exit(-1)

    elif action == 'rebuild':
        if rebuild():
            sys.exit(-1)

    else:
        print '[-] unknown command "%s"' % action
        sys.exit(-1)

    sys.exit(0)

