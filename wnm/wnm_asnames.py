#!/usr/bin/env python
# coding: utf-8

import sys, os, json, gzip
from wnm_utils import *

# =================================
# vars
# =================================
urlz = {
    'as-radb.db.gz':       'ftp://ftp.radb.net/radb/dbase/radb.db.gz',
    'as-afrinic.db.gz':    'ftp://ftp.afrinic.net/pub/dbase/afrinic.db.gz',
    'as-arin.db.gz':       'ftp://ftp.arin.net/pub/rr/arin.db',
    'as-ripe.db.gz':       'ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.aut-num.gz',
    'as-level3.db.gz':     'ftp://rr.level3.net/pub/rr/level3.db.gz',
    'as-apnic.db.gz':      'https://ftp.apnic.net/apnic/whois/apnic.db.aut-num.gz',
}

path_data   = './data-raw/'
path_db     = './data/asnames.json'

def db_download():
    count = 0
    print '=' * 40
    print '> updating AS names database'
    print '=' * 40

    for u in urlz:

        path = path_data + u
        if urlz[u][-3:] != '.gz':
            path = path_data + u[:-3]

        count += get_url(urlz[u], path)
        if urlz[u][-3:] != '.gz':
            os.system('gzip -f ' + path)

    if count != len(urlz.values()):
        print '> errors occured during update'
        return -1

    print '=' * 40
    print '> done.'

def db_update():
    out = {}

    for db in urlz:
        print '> parsing %s' % db
        with gzip.open(path_data + db, 'rb') as f:
            lines = f.read().splitlines()

        for i in range(len(lines)-1):
            l0 = lines[i]
            l1 = lines[i+1]
            if l0[0:8] != 'aut-num:' or l1[0:8] != 'as-name:':
                continue
            l0 = l0.replace('aut-num:', '').strip()
            l1 = l1.replace('as-name:', '').strip()

            if '#' in l0:
                l0 = l0[0:l0.find('#')]
            if '#' in l1:
                l1 = l1[0:l1.find('#')]

            l1 = l1.replace('DBP', '').replace('UNSPECIFIED', '')
            if not len(l1):
                continue

            asn = int(l0[2:])
            name = l1

            if asn not in out:
                out[asn] = name
            elif len(name) > len(out[asn]):
                out[asn] = name

    wnm_save(path_db, out)


def usage():
    print '%s usage <command>' % sys.argv[0]
    print ''
    print 'commands:'
    print '    download             -- download rr databases'
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
        if db_download():
            sys.exit(-1)
    elif action == 'rebuild':
        if db_update():
            sys.exit(-1)
    elif action == 'update':
        if db_download():
            sys.exit(-1)
        if db_update():
            sys.exit(-1)

