#!/usr/bin/env python
# coding: utf-8
import sys, os, json, re, glob, datetime
from wnm_utils import *

# submarine cable database
url         = 'https://github.com/telegeography/www.submarinecablemap.com/archive/master.zip'
path_raw    = './data-raw/'
path_tmp    = path_raw + 'cables.zip'
path_db     = path_raw + 'cables'
path_out    = './data/scdb.json'

def scd_download():
    print '=' * 40
    print '> updating submarine cable database'
    print '=' * 40
    if not get_url(url, path_tmp, chunk_size=512):
        # retry once, github can be annoying sometimes
        if not get_url(url, path_tmp, chunk_size=512):
            return -1

    if os.system('unzip -q -d %s %s' % (path_raw, path_tmp)):
        print '> failed to unzip %s' % path_tmp
        return -1

    if os.system('mv %s/www.submarinecablemap.com-master/public/api/v1/ %s' % (path_raw, path_db)):
        return -1

    if os.system('rm -rf %s/www.submarinecablemap.com-master' % path_raw):
        return -1

    if os.system('rm -rf %s' % path_tmp):
        return -1

    return 0

def scd_rebuild():

    def build_db_from_dir(path):
        data = []
        for f in glob.glob('%s/*' % path):
            if 'all.json' in f:
                continue
            if 'search.json' in f:
                continue
            with open(f, 'rb') as f:
                data += [ json.load(f) ]
        return data

    # country name to iso2 country code
    ccmap = {"Andorra":"AD","United Arab Emirates":"AE","Afghanistan":"AF","Antigua and Barbuda":"AG","Anguilla":"AI","Albania":"AL","Armenia":"AM","Netherlands Antilles":"AN","Angola":"AO","Antarctica":"AQ","Argentina":"AR","American Samoa":"AS","Austria":"AT","Australia":"AU","Aruba":"AW","ALA Aland Islands":"AX","Azerbaijan":"AZ","Bosnia and Herzegovina":"BA","Barbados":"BB","Bangladesh":"BD","Belgium":"BE","Burkina Faso":"BF","Bulgaria":"BG","Bahrain":"BH","Burundi":"BI","Benin":"BJ","Saint-Barthélemy":"BL","Saint Barthélemy":"BL","Bermuda":"BM","Brunei Darussalam":"BN","Brunei":"BN","Bolivia":"BO","Bonaire":"BQ","Sint Eustatius and Saba":"BQ","Brazil":"BR","Bahamas":"BS","Bhutan":"BT","Bouvet Island":"BV","Botswana":"BW","Belarus":"BY","Belize":"BZ","Canada":"CA","Cocos (Keeling) Islands":"CC","Congo, (Kinshasa)":"CD","Congo, Rep.":"CD","Congo, Dem. Rep.":"CD","Central African Republic":"CF","Congo (Brazzaville)":"CG","Switzerland":"CH","Côte d'Ivoire":"CI","Cook Islands":"CK","Chile":"CL","Cameroon":"CM","China":"CN","Colombia":"CO","Costa Rica":"CR","Cuba":"CU","Cape Verde":"CV","Curaçao":"CW","Christmas Island":"CX","Cyprus":"CY","Czech Republic":"CZ","Germany":"DE","Djibouti":"DJ","Denmark":"DK","Tyra":"DK","Valdemar":"DK","South Arne":"DK","Dominica":"DM","Dominican Republic":"DO","Algeria":"DZ","Ecuador":"EC","Estonia":"EE","Egypt":"EG","Western Sahara":"EH","Eritrea":"ER","Spain":"ES","Ethiopia":"ET","Europe":"EU","Finland":"FI","Fiji":"FJ","Falkland Islands (Malvinas)":"FK","Micronesia, Federated States of":"FM","Federated States of Micronesia":"FM","Chuuk":"FM","Faroe Islands":"FO","Faeroe Islands":"FO","France":"FR","Gabon":"GA","United Kingdom":"GB","Grenada":"GD","Georgia":"GE","French Guiana":"GF","Guernsey":"GG","Ghana":"GH","Gibraltar":"GI","Greenland":"GL","Gambia":"GM","Guinea":"GN","Guadeloupe":"GP","Equatorial Guinea":"GQ","Greece":"GR","South Georgia and the South Sandwich Islands":"GS","Guatemala":"GT","Guam":"GU","Guinea-Bissau":"GW","Guyana":"GY","Hong Kong, SAR China":"HK","Heard and Mcdonald Islands":"HM","Honduras":"HN","Croatia":"HR","Haiti":"HT","Hungary":"HU","Indonesia":"ID","Ireland":"IE","Israel":"IL","Isle of Man":"IM","India":"IN","British Indian Ocean Territory":"IO","Iraq":"IQ","Iran, Islamic Republic of":"IR","Iran":"IR","Iceland":"IS","Italy":"IT","Jersey":"JE","Jamaica":"JM","Jordan":"JO","Japan":"JP","Kenya":"KE","Kyrgyzstan":"KG","Cambodia":"KH","Kiribati":"KI","Comoros":"KM","Saint Kitts and Nevis":"KN","Korea (North)":"KP","Korea (South)":"KR","Korea, Rep.":"KR","Kuwait":"KW","Cayman Islands":"KY","Kazakhstan":"KZ","Lao PDR":"LA","Lebanon":"LB","Saint Lucia":"LC","Liechtenstein":"LI","Sri Lanka":"LK","Liberia":"LR","Lesotho":"LS","Lithuania":"LT","Luxembourg":"LU","Latvia":"LV","Libya":"LY","Morocco":"MA","Monaco":"MC","Moldova":"MD","Montenegro":"ME","Saint-Martin (French part)":"MF","Saint Martin":"MF","SaintMartin":"MF","Madagascar":"MG","Marshall Islands":"MH","Republic of Marshall Islands":"MH","Macedonia, Republic of":"MK","Mali":"ML","Myanmar":"MM","Mongolia":"MN","Macao, SAR China":"MO","Northern Mariana Islands":"MP","Saipan":"MP","Martinique":"MQ","Mauritania":"MR","Montserrat":"MS","Malta":"MT","Mauritius":"MU","Maldives":"MV","Malawi":"MW","Mexico":"MX","Malaysia":"MY","Mozambique":"MZ","Namibia":"NA","New Caledonia":"NC","Niger":"NE","Norfolk Island":"NF","Nigeria":"NG","Nicaragua":"NI","Netherlands":"NL","Norway":"NO","Nepal":"NP","Nauru":"NR","Niue":"NU","New Zealand":"NZ","Oman":"OM","Panama":"PA","Peru":"PE","French Polynesia":"PF","Papua New Guinea":"PG","Philippines":"PH","Pakistan":"PK","Poland":"PL","Saint Pierre and Miquelon":"PM","Pitcairn":"PN","Puerto Rico":"PR","Palestinian Territory":"PS","Portugal":"PT","Palau":"PW","Paraguay":"PY","Qatar":"QA","Réunion":"RE","Romania":"RO","Serbia":"RS","Russian Federation":"RU","Russia":"RU","Rwanda":"RW","Saudi Arabia":"SA","Solomon Islands":"SB","Seychelles":"SC","Sudan":"SD","Sweden":"SE","Singapore":"SG","Saint Helena":"SH","Slovenia":"SI","Svalbard and Jan Mayen Islands":"SJ","Slovakia":"SK","Sierra Leone":"SL","San Marino":"SM","Senegal":"SN","Somalia":"SO","Suriname":"SR","South Sudan":"SS","Sao Tome and Principe":"ST","El Salvador":"SV","Sint Maarten":"SX","Syrian Arab Republic":"SY","Syria":"SY","Swaziland":"SZ","Turks and Caicos Islands":"TC","Chad":"TD","French Southern Territories":"TF","Togo":"TG","Thailand":"TH","Tajikistan":"TJ","Tokelau":"TK","Timor-Leste":"TL","Turkmenistan":"TM","Tunisia":"TN","Tonga":"TO","Turkey":"TR","Trinidad and Tobago":"TT","Tuvalu":"TV","Taiwan, Republic of China":"TW","Taiwan":"TW","Tanzania, United Republic of":"TZ","Tanzania":"TZ","Ukraine":"UA","Uganda":"UG","US Minor Outlying Islands":"UM","United States of America":"US","United States":"US","Uruguay":"UY","Uzbekistan":"UZ","Holy See (Vatican City State)":"VA","Saint Vincent and Grenadines":"VC","Saint Vincent and the Grenadines":"VC","Venezuela":"VE","British Virgin Islands":"VG","Virgin Islands (U.K.)":"VG","Virgin Islands, US":"VI","Virgin Islands (U.S.)":"VI","Viet Nam":"VN","Vietnam":"VN","Vanuatu":"VU","Wallis and Futuna Islands":"WF","Wallis and Futuna":"WF","Samoa":"WS","Kosovo":"XK","Yemen":"YE","Mayotte":"YT","South Africa":"ZA","Zambia":"ZM","Zimbabwe":"ZW","Canary Islands":"ES"}

    countries = {}
    landing2cc = {}
    for cn in build_db_from_dir(path_db + '/country/'):
        n = cn['name'].encode('utf-8')
        c = {}
        c['cc']         = ccmap[n]
        c['name']       = n
        c['cables']     = [ str(_['cable_id'])          for _ in cn['cables'] ]
        c['landings']   = [ str(_['landing_point_id'])  for _ in cn['landing_points'] ]

        countries[c['cc']] = c

        for lid in c['landings']:
            if lid in landing2cc and landing2cc[lid] != c['cc']:
                print '> warning landing-point %s already mapped to %s (and %s??)' % (lid, landing2cc[lid], c['cc'])
            else:
                landing2cc[lid] = c['cc']

    landings = {}
    for ld in build_db_from_dir(path_db + '/landing-point/'):
        l = {}
        lid = str(ld['city_id'])
        l['cc']         = landing2cc[lid]
        l['id']         = lid
        l['name']       = ld['name']
        l['lat']        = ld['latitude']
        l['lng']        = ld['longitude']
        l['cables']     = [ str(_['cable_id']) for _ in ld['cables'] ]

        landings[lid] = l

    cables = {}
    for ca in build_db_from_dir(path_db + '/cable/'):
        cid = str(ca['cable_id'])

        def _length(s):
            if s == 'n.a.':
                return -1
            return float(s.replace(',', '').replace(' ', '').replace('km', ''))

        c = {}
        c['id']         = cid
        c['name']       = ca['name'].encode('utf-8')
        c['rfs']        = ca['rfs'].split(' ')[-1]
        c['length']     = _length(ca['length'])
        c['url']        = ca['url']     if ca['url']   is not None  else ''
        c['notes']      = ca['notes']   if ca['notes'] is not None  else ''
        c['landings']   = [ str(_['landing_point_id']) for _ in ca['landing_points'] ]
        c['countries']  = list(set([ landings[i]['cc'] for i in c['landings'] if i in landings ]))

        own = ca['owners'].replace(',', ', ')
        while own.find('  ') >= 0:
            own = own.replace('  ', ' ')
        c['owners']     = own.split(', ')

        # is cable ready for service?
        month = ca['rfs'].split(' ')[-2] if len(ca['rfs'].split(' ')) > 1 else 'December'
        months = { 'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12, 'Q1':3, 'Q2':6, 'Q3':9, 'Q4': 12 }
        if month not in months.keys():
            month = 'December'
        try:
            m = months[month]
            y = int(c['rfs'])
            today = datetime.date.today()

            if today.year > y:
                c['ready'] = 1
            elif today.year < y:
                c['ready'] = 0
            else:
                c['ready'] = 1 if m < today.month else 0
        except:
            c['ready'] = 0

        cables[cid] = c

    # sanity check
    for cc in countries:
        for lid in countries[cc]['landings']:
            if lid not in landings:
                print '> unknown landing %s for country %s' % (lid, cc)
                countries[cc]['landings'] = [ lid for lid in countries[cc]['landings'] if lid in landings ]
    for cid in cables:
        for lid in cables[cid]['landings']:
            if lid not in landings:
                print '> unknown landing %s for cable %s' % (lid, cid)
                cables[cid]['landings'] = [ lid for lid in cables[cid]['landings'] if lid in landings ]

    scdb = {
        'countries':    countries,
        'landings':     landings,
        'cables':       cables,
    }

    wnm_save(path_out, scdb)

    return 0


# =================================
# main
# =================================
def usage():
    print '%s usage <command>' % sys.argv[0]
    print ''
    print 'commands:'
    print '    download             -- download submarinecablemap database'
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
        scd_download()

    elif action == 'update':
        if scd_download():
            sys.exit(-1)
        if scd_rebuild():
            sys.exit(-1)

    elif action == 'rebuild':
        if scd_rebuild():
            sys.exit(-1)

    else:
        print '[-] unknown command "%s"' % action
        sys.exit(-1)

    sys.exit(0)

