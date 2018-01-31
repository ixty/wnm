#!/usr/bin/env python
# coding: utf-8
import sys, os, socket, struct, urllib2, json, bisect
from wnm_utils import *

# =================================
# vars
# =================================
nics = {
    'afrinic':  'ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest',
    'apnic':    'ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest',
    'arin':     'ftp://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest',
    'lacnic':   'ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest',
    'ripe':     'ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest',
}

path_nic    = './data-raw/'
path_data   = './data/'
path_db     = path_data + 'nics.json'
default_db  = { 'asn': {}, 'ipv4': {}, 'ipv6': {}, 'dbg': {} }
db          = default_db
keys_asn    = []
keys_ipv4   = []
keys_ipv6   = []


# =================================
# funcs
# =================================

def parse_rir(db, data):
    header = 0

    for l in data.splitlines(False):
        l = l.strip()
        # skip coments & empty lines
        if l[0] == '#' or not len(l):
            continue
        tmp = l.split('|')

        # parse header
        if not header:
            header = 1
            version, nic, records, enddate = tmp[0], tmp[1], int(tmp[3]), tmp[5]
            if version != '2' and version != '2.3':
                print '[-1] unknown version'
                return 0
            print '[%7s] date: %s records %d ' % (nic, enddate, records)
            continue

        # parse summary lines
        if tmp[-1] == 'summary':
            continue

        # normal entry
        fields = ['registry', 'cc', 'type', 'start', 'value', 'date', 'status', 'extensions']
        entry = dict(zip(fields, tmp))

        entry['intstart']   = val_to_int(entry['type'], entry['start'])
        entry['count']      = int(entry['value'])
        entry['reg']        = nic

        # add it based on type
        if entry['type'] == 'ipv4':
            startval = ipv4_to_int(entry['start'])
            entry['cidr'] = entry['start']
            for i in range(32):
                if (1 << i) == entry['count']:
                    entry['cidr'] += '/%d' % (32 - i)
                    break
            if not '/' in entry['cidr']:
                entry['cidr'] += '/?'
        elif entry['type'] == 'ipv6':
            startval = ipv6_to_int(entry['start'])
            entry['count'] = 1 << (128 - int(entry['value']))
            entry['cidr'] = entry['start'] + '/' + entry['value']
        else:
            startval = int(entry['start'])
            for i in range(int(startval) + 1, int(startval) + int(entry['count'])):
                db[entry['type']][str(i)] = entry


        db[entry['type']][startval] = entry

    return db

def db_download():
    count = 0
    print '=' * 40
    print '> updating nics database'
    print '=' * 40

    for u in nics:
        count += get_url(nics[u], path_nic + 'nic-' + u + '.txt')

    if count != len(nics):
        print '> errors occured during update'
        return -1

    return 0

def db_consolidate(db):

    print '=' * 40
    print '> consolidating database..'

    for f in nics:
        with open(path_nic + 'nic-' + f + '.txt', 'rb') as f:
            parse_rir(db, f.read())

    print '> total rirs info [asn: %d, ipv4: %d, ipv6: %d]' % (len(db['asn']), len(db['ipv4']), len(db['ipv6']))

    wnm_save(path_db, db)

def db_update(download=1):
    if download:
        if db_download() < 0:
            return -1

    db_consolidate(default_db)
    return 0

def db_load():
    global db
    try:
        db1 = wnm_load(path_db)
        for type in ['asn', 'ipv4', 'ipv6']:
            for k in db1[type]:
                db[type][int(k)] = db1[type][k]
        print '> loaded db (asn: %d, ipv4: %d, ipv6: %d)' % (len(db['asn']), len(db['ipv4']), len(db['ipv6']))
        return db
    except:
        print '[-] error loading database file'
        return default_db


def lookup(type, val, warn=1):
    global keys_ipv4, keys_ipv6, keys_asn

    # build sorted key tables if needed
    if type == 'ipv4':
        if not len(keys_ipv4):
            keys_ipv4 = sorted(db['ipv4'].keys())
        keys = keys_ipv4
    elif type == 'ipv6':
        if not len(keys_ipv6):
            keys_ipv6 = sorted(db['ipv6'].keys())
        keys = keys_ipv6
    else:
        if not len(keys_asn):
            keys_asn = sorted(db['asn'].keys())
        keys = keys_asn

    # convert to decimal
    intval = val_to_int(type, val)

    # lookup
    ind = bisect.bisect_left(keys, intval)
    if ind < len(keys):
        if keys[ind] == intval:
            return db[type][keys[ind]]
        else:
            e = db[type][keys[ind-1]]
            if intval >= e['intstart'] and intval < e['intstart'] + e['count']:
                return e

    if warn:
        print '[-] cant resolve [%s:%s]' % (type, val)
    return None

def lookup_ipv4(ipv4):
    return lookup('ipv4', ipv4)

def lookup_ipv6(ipv6):
    return lookup('ipv6', ipv6)

def lookup_asn(asn):
    return lookup('asn', asn)


# =================================
# main
# =================================
def usage():
    print '%s usage <command>' % sys.argv[0]
    print ''
    print 'commands:'
    print '    download             -- download nics database'
    print '    rebuild              -- rebuild local json database'
    print '    update               -- download & rebuild'
    print '    lookup ipv4_addr     -- lookup an ipv4 address'
    print '    lookup ipv4 addr     -- lookup an ipv4 address'
    print '    lookup ipv6 addr     -- lookup an ipv6 address'
    print '    lookup asn  addr     -- lookup an AS number'
    print
    sys.exit(1)

if __name__ == '__main__':
    if not os.path.exists(path_nic):
        os.mkdir(path_nic)

    if not os.path.exists(path_data):
        os.mkdir(path_data)

    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    action = sys.argv[1]
    if action == 'download':
        if db_download():
            sys.exit(-1)
    elif action == 'update':
        if db_update():
            sys.exit(-1)
    elif action == 'rebuild':
        if db_update(0):
            sys.exit(-1)
    elif action == 'lookup':
        if len(sys.argv) == 3:
            type = 'ipv4'
            val = sys.argv[2]
        elif len(sys.argv) == 4:
            type = sys.argv[2]
            val = sys.argv[3]
        else:
            usage()
        db_load()
        print json.dumps(lookup(type, val), indent=4)
    else:
        print '[-] unknown command "%s"' % action
        sys.exit(-1)

    sys.exit(0)



