#!/usr/bin/env python
# coding: utf-8
import json, math, copy, re, itertools, os, gzip
import flask, flask_compress, jinja2
import pwui_jinja, pwui_pages, pwui_tools

# debug mode?
debug   = 1             if 'DEBUG' in os.environ and int(os.environ['DEBUG']) else 0
addr    = '127.0.0.1'   if debug else '0.0.0.0'
# port    = 5000
port    = 80

# load our database
print('> loading database')
with gzip.open('./data/final.json.gz', 'rb') as f:
    db = json.load(f)

# options
cache_enabled = not debug

# init flask app
print('> starting web server')
app = flask.Flask('wnm', static_folder='res', template_folder='html')

# auto reload templates + static files
app.config['TEMPLATES_AUTO_RELOAD'] = 1

import pwui_routes

# add content compression
flask_compress.Compress(app)

# run interface
if debug:
    app.run(host=addr, port=port, threaded=True)
else:
    from gevent.wsgi import WSGIServer
    srv = WSGIServer((addr, port), app)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print '> stop.'
