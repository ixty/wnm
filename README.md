# World Net Map
2017-2018 - Martin Balch - <a href="mailto:martin.balch+wnm@gmail.com">contact</a>

## intro

World Net Map (WNM) is a project to visualize geographically the internet infrastructure, networks and connectivity.
It uses data from multiple sources to display information on networks, countries, facilities, exchanges, submarine cables, ... and represent everything in a single interactive map.
This repository hosts the code used to download, agregate, consolidate & format the data (`wnm_*`) in addition to the code of a web server that displays the data (`pwui_*`).

See it in action here: [http://wnm.ixty.net/](http://wnm.ixty.net/)

![World Net Map Screenshot](https://github.com/ixty/wnm/raw/master/screenshot.png "World Net Map Screenshot")

## installation

```shell
# pre-requisites
$ sudo apt-get install git virtualenv unzip

# install with data (recommended)
$ git clone --recursive https://github.com/ixty/wnm

# or install without data (you need to regenerate databases)
$ # git clone https://github.com/ixty/wnm

# python requirements
$ cd wnm
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## regenerate databases

### automated update
If you want to generate or update the database used by WNM, you can use the following command:
```shell
$ source venv/bin/activate
$ ./update.py
```
This operation can take a long time based on your bandwith & cpu.

### manual sub-database updates
You can also update specific databases by using the following scripts:
```shell
$ ./wnm/wnm_asnames.py
$ ./wnm/wnm_bgp.py
$ ./wnm/wnm_geo.py
$ ./wnm/wnm_nics.py
$ ./wnm/wnm_scd.py
$ ./wnm/wnm_world.py
```
They all have the same usage: `./script <download | rebuild | update>`
- `download` will download the raw source data
- `rebuild` will update our local database (./data/*) with the previously downloaded source data.
- `update` is equivalent to running `download` and `rebuild`

### geo-location
To get accurate positioning for facilities, you will need to get an OpenCageData API key from [OpenCageData.com](https://geocoder.opencagedata.com/api)
```shell
# for a first build
$ OCD_KEY=01234567890123456789012345678901 ./update.py

# or just regenerate WNM data
$ OCD_KEY=01234567890123456789012345678901 ./wnm/wnm_merge.py
```

### update log
<details>
    <summary>Example output of the full updating process</summary>
```
========================================
> updating AS names database
========================================
> ftp://ftp.radb.net/radb/dbase/radb.db.gz
> downloaded ./data-raw/as-radb.db.gz in 3.2 secs
> ftp://ftp.arin.net/pub/rr/arin.db
> downloaded ./data-raw/as-arin.db in 5.4 secs
> ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.aut-num.gz
> downloaded ./data-raw/as-ripe.db.gz in 2.2 secs
> ftp://ftp.afrinic.net/pub/dbase/afrinic.db.gz
> downloaded ./data-raw/as-afrinic.db.gz in 4.4 secs
> ftp://rr.level3.net/pub/rr/level3.db.gz
> downloaded ./data-raw/as-level3.db.gz in 3.1 secs
> https://ftp.apnic.net/apnic/whois/apnic.db.aut-num.gz
> downloaded ./data-raw/as-apnic.db.gz in 6.6 secs
========================================
> done.
> parsing as-radb.db.gz
> parsing as-arin.db.gz
> parsing as-ripe.db.gz
> parsing as-afrinic.db.gz
> parsing as-level3.db.gz
> parsing as-apnic.db.gz
> saving to ./data/asnames.json.gz (52112 items)

========================================
> updating BGP database
========================================
> http://routeviews.org/route-views.linx/bgpdata/2018.01/RIBS/rib.20180129.0000.bz2
> downloaded ./data-raw/bgp-linx.bz2 in 9.3 secs
> downloaded [linx] bgp database.
> http://routeviews.org/route-views.eqix/bgpdata/2018.01/RIBS/rib.20180129.0000.bz2
> downloaded ./data-raw/bgp-eqix.bz2 in 4.7 secs
> downloaded [eqix] bgp database.
> http://routeviews.org/route-views.jinx/bgpdata/2018.01/RIBS/rib.20180129.0000.bz2
> downloaded ./data-raw/bgp-jinx.bz2 in 2.3 secs
> downloaded [jinx] bgp database.
> http://routeviews.org/route-views.saopaulo/bgpdata/2018.01/RIBS/rib.20180129.0000.bz2
> downloaded ./data-raw/bgp-saopaulo.bz2 in 4.1 secs
> downloaded [saopaulo] bgp database.
> http://routeviews.org/route-views.sg/bgpdata/2018.01/RIBS/rib.20180129.0000.bz2
> downloaded ./data-raw/bgp-sg.bz2 in 3.3 secs
> downloaded [sg] bgp database.
> done 5/5
> loading ./data-raw/bgp-linx.bz2
> processing ./data-raw/bgp-linx.bz2
100%|████████████████████████████████████████████| 16948716/16948716 [32:26<00:00, 8707.87it/s]
> loading ./data-raw/bgp-eqix.bz2
> processing ./data-raw/bgp-eqix.bz2
100%|██████████████████████████████████████████████| 8601056/8601056 [18:27<00:00, 7766.23it/s]
> loading ./data-raw/bgp-jinx.bz2
> processing ./data-raw/bgp-jinx.bz2
100%|██████████████████████████████████████████████| 1157353/1157353 [02:29<00:00, 7748.20it/s]
> loading ./data-raw/bgp-saopaulo.bz2
> processing ./data-raw/bgp-saopaulo.bz2
100%|██████████████████████████████████████████████| 9463089/9463089 [24:37<00:00, 6404.86it/s]
> loading ./data-raw/bgp-sg.bz2
> processing ./data-raw/bgp-sg.bz2
100%|██████████████████████████████████████████████| 4093937/4093937 [09:39<00:00, 7061.49it/s]
> saving to ./data/bgp.json.gz (60826 items)

========================================
> updating world cities database
========================================
> http://download.maxmind.com/download/worldcities/worldcitiespop.txt.gz
> downloaded ./data-raw/worldcitiespop.txt.gz in 3.4 secs
> done
> processing ./data-raw/worldcitiespop.txt.gz
> saving to ./data/cities.json.gz (234 items)

========================================
> updating nics database
========================================
> ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest
> downloaded ./data-raw/nic-lacnic.txt in 6.3 secs
> ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
> downloaded ./data-raw/nic-apnic.txt in 10.1 secs
> ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest
> downloaded ./data-raw/nic-afrinic.txt in 3.1 secs
> ftp://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest
> downloaded ./data-raw/nic-arin.txt in 16.6 secs
> ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest
> downloaded ./data-raw/nic-ripe.txt in 1.5 secs
========================================
> consolidating database..
[ lacnic] date: 20180126 records 29128
[  apnic] date: 20180129 records 54420
[afrinic] date: 20180129 records 5652
[   arin] date: 20180129 records 137492
[ripencc] date: 20180128 records 114677
> total rirs info [asn: 85628, ipv4: 183252, ipv6: 81081]
> saving to ./data/nics.json.gz (4 items)

========================================
> updating submarine cable database
========================================
> https://github.com/telegeography/www.submarinecablemap.com/archive/master.zip
> error downloading ./data-raw/cables.zip
> https://github.com/telegeography/www.submarinecablemap.com/archive/master.zip
> downloaded ./data-raw/cables.zip in 1.3 secs
> unknown landing 9595 for country ID
> unknown landing 9595 for cable 1895
> saving to ./data/scdb.json.gz (3 items)

========================================
> updating country database
========================================
> http://download.geonames.org/export/dump/countryInfo.txt
> downloaded ./data-raw/worldinfo.txt in 0.1 secs
> saving to ./data/worldinfo.json.gz (252 items)

========================================
> updating PeeringDB
========================================
Operations to perform:
  Synchronize unmigrated apps: django_peeringdb
  Apply all migrations: (none)
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
  Installing custom SQL...
Running migrations:
  No migrations to apply.
org last update 1517240845 0 changed
data to be processed 0
fac last update 1517069653 0 changed
data to be processed 0
net last update 1517244409 3 changed
data to be processed 3
ix last update 1517005124 0 changed
data to be processed 0
ixfac last update 1516870316 0 changed
data to be processed 0
ixlan last update 1516870415 0 changed
data to be processed 0
ixpfx last update 1516707274 0 changed
data to be processed 0
poc last update 1517066523 5 changed
data to be processed 5
netfac last update 1517235749 0 changed
data to be processed 0
netixlan last update 1517242057 3 changed
data to be processed 3

========================================
> Merging databases
========================================
> loading data from data/nics.json.gz
> loading data from data/bgp.json.gz
> loading data from data/scdb.json.gz
> loading data from data/asnames.json.gz
> loading data from data/cities.json.gz
> loading data from data/worldinfo.json.gz
> loading peering db ..
> merging network info ..
> enriching networks ..
> enriching facilities ..
> loading data from data/geofacs.json.gz
> error loading data/geofacs.json.gz
> warn: set OpenCageData API key (export OCD_KEY=...) for accurate geolocation
> saving to data/geofacs.json.gz (0 items)

> enriching IXs ..
> building country stats ..
> saving to data/final.json.gz (6 items)

> all done :) (102m 4s)
```
</details>

## run server
The default bound address is `0.0.0.0:80` in release mode, which may requires root acess.
```shell
$ source venv/bin/activate
$ ./pwui/pwui.py
```

### debug mode
In debug mode, the default bound address is `127.0.0.1:5000`, flask is used as a webserver, templates are automatically reloaded and there is no cache on pages.

```shell
$ source venv/bin/activate
$ DEBUG=1 ./pwui/pwui.py
```

## data sources
This is the list of all "data-raw" files that we use as data sources for WNM.

### RIRs
```shell
./data-raw/nic-afrinic.txt          # ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest
./data-raw/nic-apnic.txt            # ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest
./data-raw/nic-arin.txt             # ftp://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest
./data-raw/nic-lacnic.txt           # ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest
./data-raw/nic-ripe.txt             # ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest
```
Info is consolidated to `./data/nics.json.gz`

### peeringdb (peeringdb.org)
```shell
./data-raw/peeringdb.sqlite         # https://peeringdb.github.io/peeringdb-py/cli/
```
Used by `wnm_merge.py` as one of the most important databases

### telegeography (telegeography.com)
```shell
./data-raw/cables/*                 # https://github.com/telegeography/www.submarinecablemap.com
```
Info is consolidated to `./data/scdb.json.gz`

### BGP views (routeviews.org)
```shell
./data-raw/bgp-eqix.bz2             # http://routeviews.org/route-views.eqix/bgpdata/YYYY.MM/RIBS/rib.YYYYMMDD.HHMM.bz2
./data-raw/bgp-jinx.bz2             # http://routeviews.org/route-views.jinx/bgpdata/YYYY.MM/RIBS/rib.YYYYMMDD.HHMM.bz2
./data-raw/bgp-linx.bz2             # http://routeviews.org/route-views.linx/bgpdata/YYYY.MM/RIBS/rib.YYYYMMDD.HHMM.bz2
./data-raw/bgp-saopaulo.bz2         # http://routeviews.org/route-views.saopaulo/bgpdata/YYYY.MM/RIBS/rib.YYYYMMDD.HHMM.bz2
./data-raw/bgp-sg.bz2               # http://routeviews.org/route-views.sg/bgpdata/YYYY.MM/RIBS/rib.YYYYMMDD.HHMM.bz2
```
Info is consolidated to `./data/bgp.json.gz`

### world info (geonames.org)
```shell
./data-raw/worldinfo.txt            # http://download.geonames.org/export/dump/countryInfo.txt
```
Info is consolidated to `./data/worldinfo.json.gz`

### world cities (maxmind.org)
```shell
./data-raw/worldcitiespop.txt.gz    # http://download.maxmind.com/download/worldcities/worldcitiespop.txt.gz
```
Info is consolidated to `./data/worldcitiespop.txt.gz`

### AS names
```shell
./data-raw/as-afrinic.db.gz         # ftp://ftp.afrinic.net/pub/dbase/afrinic.db.gz
./data-raw/as-apnic.db.gz           # https://ftp.apnic.net/apnic/whois/apnic.db.aut-num.gz
./data-raw/as-arin.db.gz            # ftp://ftp.arin.net/pub/rr/arin.db
./data-raw/as-level3.db.gz          # ftp://rr.level3.net/pub/rr/level3.db.gz
./data-raw/as-radb.db.gz            # ftp://ftp.radb.net/radb/dbase/radb.db.gz
./data-raw/as-ripe.db.gz            # ftp://ftp.ripe.net/ripe/dbase/split/ripe.db.aut-num.gz
```
Info is consolidated to `./data/asnames.json.gz`


## Consolidated data

All our consolidated data is stored in `./wnm/data/`.
The only file directly used by the web interface is `final.json.gz` which is the consolidation of all the others in the folder.

Here is the list of all WNM databases:
    - final.json.gz             # merged database directly usable by pwui

    - asnames.json.gz           # AS number to AS name
    - bgp.json.gz               # AS bgp routes, associated prefix & routing chains
    - cities.json.gz            # world cities with country & gps coordinates
    - geofacs.json.gz           # gps coordinates for all peeringdb facilities
    - nics.json.gz              # RIR info: ASN, IPv4 & IPv6 association to countries
    - scdb.json.gz              # extract of submarinecablemap.org database in our format
    - worldinfo.json.gz         # countries surface, population, etc.

## display / pwui.py

To display the map, the `pwui` python flask app was created.
It uses [datamaps.js](http://datamaps.github.io/) (which itself uses [d3.js](https://d3js.org/)) for the world map.
It uses [bootstrap](https://getbootstrap.com/) for the layout.

## repository tree overview

```shell
wnm
╷
├── bins                # bgpdump utility
├── wnm                 # data fetching, consolidation & processing python scripts
│
├── data                # our consolidated databases in json format
│                       # (git clone https://github.com/ixty/wnm_data)
├── data-raw            # raw data from open sources
│                       # (git clone https://github.com/ixty/wnm_data-raw)
│
├── update.sh           # script to update all our local databases
│
├── html                # web interface flask templates
├── pwui                # web interface python code
├── res                 # web interface static files
│
├── requirements.txt    # python dependencies
└── README.md           # documentation
```

