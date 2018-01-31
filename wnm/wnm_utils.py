#!/usr/bin/env python
# coding: utf-8
import os, sys, json, struct, urllib, urllib2, socket, time, string, gzip

def h2bin(x):
    return x.replace(' ', '').replace('\n', '').decode('hex')

def hdstr(x):
    return ''.join( [ '%.2x' % ord(c) for c in x] )

def ascii_clean(s):
    return filter(lambda x: x in string.printable, s)

def get_url(url, fname, chunk_size=8192*16):
    def report(size_dled, size_tot, error=0):
        sys.stdout.write(' ' * 80 + '\r')
        if error:
            sys.stdout.write('> error downloading %s' % fname + '\n')
        elif size_dled >= size_tot:
            te = time.time()
            sys.stdout.write('> downloaded %s in %.1f secs' % (fname, te-ts) + '\n')
        else:
            sys.stdout.write('> downloading %s progress %.1f%%\r' % (fname, 100.0 * float(size_dled) / size_tot))
        sys.stdout.flush()

    try:
        print '> %s' % url
        ts = time.time()
        f = open(fname, 'wb+')
        ans = urllib2.urlopen(url);
        size_tot = int(ans.info().getheader('Content-Length').strip())
        size_dled = 0
        while 1:
            chunk = ans.read(chunk_size)
            if not chunk:
                break
            size_dled += len(chunk)
            f.write(chunk)
            if size_dled < size_tot:
                report(size_dled, size_tot)
        report(size_dled, size_tot)
        f.close()
        return 1
    except:
        report(0, 0, 1)
        return 0

def ipv4_to_int(ipstr):
    return struct.unpack('!I', socket.inet_pton(socket.AF_INET, ipstr))[0]

def int_to_ipv4(ipint):
    return socket.inet_ntop(socket.AF_INET, struct.pack('!I', ipint))

def ipv6_to_int(ipstr):
    _str = socket.inet_pton(socket.AF_INET6, ipstr)
    a, b = struct.unpack('!2Q', _str)
    return (a << 64) | b

def int_to_ipv6(ipint):
    a = ipint >> 64
    b = ipint & ((1 << 64) - 1)
    return socket.inet_ntop(socket.AF_INET6, struct.pack('!2Q', a, b))

def val_to_int(type, val):
    if type == 'ipv4':
        return ipv4_to_int(val)
    elif type == 'ipv6':
        return ipv6_to_int(val)
    else:
        return int(val)

def wnm_save(path, obj):
    print '> saving to %s.gz (%d items)\n' % (path, len(obj))
    with gzip.open(path + '.gz', 'wb+') as f:
        json.dump(obj, f, indent=4, sort_keys=1)

def wnm_load(path, default=None):
    try:
        print '> loading data from %s.gz' % path
        with gzip.open(path + '.gz', 'rb') as f:
            return json.load(f)
    except:
        print '> error loading %s.gz' % path
        return default

# opencagedata.com to resolve address to gps coords
# OCD_KEY=4b8c2a0d3c624c0a13c276f9125b14aa
api_warn = 0
def geo_lookup(place):
    if not 'OCD_KEY' in os.environ:
        global api_warn
        if not api_warn:
            print '> warn: set OpenCageData API key (export OCD_KEY=...) for accurate geolocation'
        api_warn = 1
        raise Exception('')

    API_KEY = os.environ['OCD_KEY']
    u = 'http://api.opencagedata.com/geocode/v1/json?q=%s&key=%s' % (urllib.quote_plus(place), API_KEY)
    a = urllib2.urlopen(u)
    r = json.loads(a.read())

    # debug
    # print '> %s' % place
    # print '> %s' % u
    # print json.dumps(r, indent=4)

    lat = r['results'][0]['geometry']['lat']
    lng = r['results'][0]['geometry']['lng']
    return (lat, lng)
