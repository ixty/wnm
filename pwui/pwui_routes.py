#!/usr/bin/env python
# coding: utf-8
import sys, re, flask
from pwui_tools     import *
from pwui_pages     import *
from pwui_colors    import *

main    = sys.modules['.'.join(__name__.split('.')[:-1]) or '__main__']
db      = main.db
colors  = pwui_colors
app     = main.app

# =========================================================================== #
# simple cache, no timeout
# =========================================================================== #
class cached(object):

    def __init__(self, timeout=None):
        self.cache = {}

    def __call__(self, func):
        def decorator(*args, **kwargs):
            if main.cache_enabled:
                if flask.request.path in self.cache:
                    return self.cache[flask.request.path]

                self.cache[flask.request.path] = func(*args, **kwargs)
                return self.cache[flask.request.path]
            else:
                return func(*args, **kwargs)

        decorator.func_name = func.func_name
        return decorator


# =========================================================================== #
# flask routes
# =========================================================================== #
@app.route("/")
def page_index():
    return flask.redirect('/ranks/world', code=302)

@app.route("/home")
def page_home():
    p = {
        'pagename': 'home',
        'reqip': flask.request.remote_addr
    }
    return flask.render_template('home.html', page=p, colors=colors)

@app.route("/data")
@cached()
def page_data():
    p = {
        'pagename':     'data',
        'countries':    [ cc for cc in db['countries'] ]
    }
    return flask.render_template('data.html', page=p, db=db, colors=colors)

@app.route('/ranks/<key>')
@app.route('/ranks/<key>/<opt>')
@cached()
def map_ranks(key='nets_loc', opt=''):
    if len(opt) > 0 and opt != 'pop' and opt != 'lnd':
        return flask.abort(404)

    page = pagedata_rank(db, key, opt)
    return flask.render_template('view_world.html', page=page, colors=colors)

@app.route('/net/<asn>')
@cached()
def map_net(asn):
    if not asn in db['nets']:
        return flask.abort(404)

    p = pagedata_net(db, asn)
    return flask.render_template('view_net.html', page=p, net=db['nets'][asn], db=db, colors=colors)

@app.route('/country/<cc>')
@cached()
def map_country(cc):
    if cc.upper() not in db['countries']:
        return flask.abort(404)

    p = pagedata_country(db, cc.upper())
    return flask.render_template('view_country.html', page=p, country=db['countries'][cc.upper()], db=db, colors=colors)

@app.route('/fac/<fid>')
@cached()
def map_fac(fid):
    if fid not in db['facilities']:
        return flask.abort(404)

    p = pagedata_fac(db, fid)
    return flask.render_template('view_fac.html', page=p, fac=db['facilities'][fid], db=db, colors=colors)

@app.route('/ix/<xid>')
@cached()
def map_ix(xid):
    if xid not in db['ixs']:
        return flask.abort(404)

    p = pagedata_ix(db, xid)
    return flask.render_template('view_ix.html', page=p, ix=db['ixs'][xid], db=db, colors=colors)

@app.route('/cable/<cid>')
@cached()
def map_cable(cid):
    if cid not in db['cables']:
        return flask.abort(404)

    p = pagedata_cable(db, cid)
    return flask.render_template('view_cable.html', page=p, cable=db['cables'][cid], db=db, colors=colors)

@app.route('/landing/<lid>')
@cached()
def map_landing(lid):
    if lid not in db['landings']:
        return flask.abort(404)

    p = pagedata_landing(db, lid)
    return flask.render_template('view_landing.html', page=p, landing=db['landings'][lid], db=db, colors=colors)

@app.route('/redir/<iso3>')
@cached()
def iso3_redir(iso3):
    for cc in db['countries']:
        if db['countries'][cc]['iso3'] == iso3:
            return flask.redirect('/country/' + cc, code=302)
    flask.abort(404)

@app.route('/ip/<cidr>')
@cached()
def redir_ip(cidr):
    ripv4 = r'^((2[0-5]{2}|2[0-4]\d|1\d{2}|[1-9]\d|\d)\.){3}(2[0-5]{2}|2[0-4]\d|1\d{2}|[1-9]\d|\d)(/(3[012]|[12]\d|\d))?$'
    ripv6 = r'^s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:)))(%.+)?s*(\/([0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-8]))?$'

    # lookup ipv4 or cidr
    is_ipv4 = re.match(ripv4, cidr)
    is_ipv6 = re.match(ripv6, cidr)
    if is_ipv4 or is_ipv6:
        for asn in lookup_cidr(db, cidr, is_ipv6):
            return flask.redirect('/net/%s' % asn, code=302)
    flask.abort(404)

@app.route('/top/<table>/<key>/<limit>')
@cached()
def top_data(table, key, limit):
    lst = db[table].values()
    lst = sorted(lst, key=lambda n: len(n[key]) if isinstance(n[key], list) else n[key], reverse=1)
    if limit != 'all':
        lst = lst[:int(limit)]
    return flask.jsonify(lst)

@app.route('/search/<path:text>')
@cached()
def search(text):
    text = text.strip()
    print '> searching for "%s"' % text

    ripv4 = r'^((2[0-5]{2}|2[0-4]\d|1\d{2}|[1-9]\d|\d)\.){3}(2[0-5]{2}|2[0-4]\d|1\d{2}|[1-9]\d|\d)(/(3[012]|[12]\d|\d))?$'
    ripv6 = r'^s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]d|1dd|[1-9]?d)(.(25[0-5]|2[0-4]d|1dd|[1-9]?d)){3}))|:)))(%.+)?s*(\/([0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-8]))?$'
    rasn  = r'^(?:as|AS|As|aS)?\s?_?(\d+)$'

    res = [];
    def add_res(type, cc, name, path):
        res.append({
            'type': type,
            'cc':   cc,
            'name': name,
            'path': path
        })

    # lookup ipv4 or cidr
    is_ipv4 = re.match(ripv4, text)
    is_ipv6 = re.match(ripv6, text)
    if is_ipv4 or is_ipv6:
        print '> cidr match %s' % text
        for asn in lookup_cidr(db, text, is_ipv6):
            net = db['nets'][asn]
            add_res('net', net['cc'], net['name'], '/net/' + asn)

    # lookup country / cc
    if len(text) == 2:
        cc = text.upper()
        if cc in db['countries']:
            add_res('country', db['countries'][cc]['cc'], db['countries'][cc]['name'], '/country/' + cc)
    else:
        for cc in db['countries']:
            if text.lower() in db['countries'][cc]['name'].lower():
                add_res('country', db['countries'][cc]['cc'], db['countries'][cc]['name'], '/country/' + cc)

    # lookup cable name
    for cid in db['cables']:
        if text.lower() in db['cables'][cid]['name'].lower():
            add_res('cable', '??', db['cables'][cid]['name'], '/cable/%s' % cid)
            continue
        # and cable owners
        for o in db['cables'][cid]['owners']:
            if text.lower() in o.lower():
                add_res('cable', '??', db['cables'][cid]['name'], '/cable/%s' % cid)
                continue

    # lookup ix name
    for xid in db['ixs']:
        if text.lower() in db['ixs'][xid]['name'].lower():
            add_res('ix', db['ixs'][xid]['country'], db['ixs'][xid]['name'], '/ix/%s' % xid)

    # lookup fac name
    for fid in db['facilities']:
        if text.lower() in db['facilities'][fid]['name'].lower():
            add_res('facility', db['facilities'][fid]['country'], db['facilities'][fid]['name'], '/fac/%s' % fid)

    # lookup landing name
    for lid in db['landings']:
        if text.lower() in db['landings'][lid]['name'].lower():
            add_res('landing', db['landings'][lid]['cc'], db['landings'][lid]['name'], '/landing/%s' % lid)

    # lookup AS
    asm = re.match(rasn, text)
    if asm:
        asn = asm.group(1)
        print '> AS match %s' % asn
        if asn in db['nets']:
            add_res('net', db['nets'][asn]['cc'], db['nets'][asn]['name'], '/net/' + asn)

    # as name
    for asn in db['nets']:
        if text.lower() in db['nets'][asn]['name'].lower():
            add_res('net', db['nets'][asn]['cc'], db['nets'][asn]['name'], '/net/' + asn)


    return flask.render_template('search_res.html', search_res=res, colors=colors)
