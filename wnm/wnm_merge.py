#!/usr/bin/env python
# coding: utf-8
import os, sys, json, sqlite3, netaddr, unidecode, math
from wnm_utils import wnm_load, wnm_save, geo_lookup

# country codes iso2 -> iso3
iso3        = {"AD":"AND","AE":"ARE","AF":"AFG","AG":"ATG","AI":"AIA","AL":"ALB","AM":"ARM","AO":"AGO","AQ":"ATA","AR":"ARG","AS":"ASM","AT":"AUT","AU":"AUS","AW":"ABW","AX":"ALA","AZ":"AZE","BA":"BIH","BB":"BRB","BD":"BGD","BE":"BEL","BF":"BFA","BG":"BGR","BH":"BHR","BI":"BDI","BJ":"BEN","BL":"BLM","BM":"BMU","BN":"BRN","BO":"BOL","BQ":"BES","BR":"BRA","BS":"BHS","BT":"BTN","BV":"BVT","BW":"BWA","BY":"BLR","BZ":"BLZ","CA":"CAN","CC":"CCK","CD":"COD","CF":"CAF","CG":"COG","CH":"CHE","CI":"CIV","CK":"COK","CL":"CHL","CM":"CMR","CN":"CHN","CO":"COL","CR":"CRI","CU":"CUB","CV":"CPV","CW":"CUW","CX":"CXR","CY":"CYP","CZ":"CZE","DE":"DEU","DJ":"DJI","DK":"DNK","DM":"DMA","DO":"DOM","DZ":"DZA","EC":"ECU","EE":"EST","EG":"EGY","EH":"ESH","ER":"ERI","ES":"ESP","ET":"ETH","EU":"EUU","FI":"FIN","FJ":"FJI","FK":"FLK","FM":"FSM","FO":"FRO","FR":"FRA","GA":"GAB","GB":"GBR","GD":"GRD","GE":"GEO","GF":"GUF","GG":"GGY","GH":"GHA","GI":"GIB","GL":"GRL","GM":"GMB","GN":"GIN","GP":"GLP","GQ":"GNQ","GR":"GRC","GS":"SGS","GT":"GTM","GU":"GUM","GW":"GNB","GY":"GUY","HK":"HKG","HM":"HMD","HN":"HND","HR":"HRV","HT":"HTI","HU":"HUN","ID":"IDN","IE":"IRL","IL":"ISR","IM":"IMN","IN":"IND","IO":"IOT","IQ":"IRQ","IR":"IRN","IS":"ISL","IT":"ITA","JE":"JEY","JM":"JAM","JO":"JOR","JP":"JPN","KE":"KEN","KG":"KGZ","KH":"KHM","KI":"KIR","KM":"COM","KN":"KNA","KP":"PRK","KR":"KOR","KW":"KWT","KY":"CYM","KZ":"KAZ","LA":"LAO","LB":"LBN","LC":"LCA","LI":"LIE","LK":"LKA","LR":"LBR","LS":"LSO","LT":"LTU","LU":"LUX","LV":"LVA","LY":"LBY","MA":"MAR","MC":"MCO","MD":"MDA","ME":"MNE","MF":"MAF","MG":"MDG","MH":"MHL","MK":"MKD","ML":"MLI","MM":"MMR","MN":"MNG","MO":"MAC","MP":"MNP","MQ":"MTQ","MR":"MRT","MS":"MSR","MT":"MLT","MU":"MUS","MV":"MDV","MW":"MWI","MX":"MEX","MY":"MYS","MZ":"MOZ","NA":"NAM","NC":"NCL","NE":"NER","NF":"NFK","NG":"NGA","NI":"NIC","NL":"NLD","NO":"NOR","NP":"NPL","NR":"NRU","NU":"NIU","NZ":"NZL","OM":"OMN","PA":"PAN","PE":"PER","PF":"PYF","PG":"PNG","PH":"PHL","PK":"PAK","PL":"POL","PM":"SPM","PN":"PCN","PR":"PRI","PS":"PSE","PT":"PRT","PW":"PLW","PY":"PRY","QA":"QAT","RE":"REU","RO":"ROU","RS":"SRB","RU":"RUS","RW":"RWA","SA":"SAU","SB":"SLB","SC":"SYC","SD":"SDN","SE":"SWE","SG":"SGP","SH":"SHN","SI":"SVN","SJ":"SJM","SK":"SVK","SL":"SLE","SM":"SMR","SN":"SEN","SO":"SOM","SR":"SUR","SS":"SSD","ST":"STP","SV":"SLV","SX":"SXM","SY":"SYR","SZ":"SWZ","TC":"TCA","TD":"TCD","TF":"ATF","TG":"TGO","TH":"THA","TJ":"TJK","TK":"TKL","TL":"TLS","TM":"TKM","TN":"TUN","TO":"TON","TR":"TUR","TT":"TTO","TV":"TUV","TW":"TWN","TZ":"TZA","UA":"UKR","UG":"UGA","UM":"UMI","US":"USA","UY":"URY","UZ":"UZB","VA":"VAT","VC":"VCT","VE":"VEN","VG":"VGB","VI":"VIR","VN":"VNM","VU":"VUT","WF":"WLF","WS":"WSM","XK":"XKX","YE":"YEM","YT":"MYT","ZA":"ZAF","ZM":"ZMB","ZW":"ZWE","AP":"APR"}
# country centroids
cc_gps      = {"AD":[42.5,1.5],"AE":[24,54],"AF":[33,66],"AG":[17.05,-61.8],"AI":[18.216667,-63.05],"AL":[41,20],"AM":[40,45],"AO":[-12.5,18.5],"AR":[-34,-64],"AS":[-14.3333333,-170],"AT":[47.333333,13.333333],"AU":[-25,135],"AW":[12.5,-69.966667],"AZ":[40.5,47.5],"AX":[60.2012029,19.8022369],"BA":[44.25,17.833333],"BB":[13.166667,-59.533333],"BD":[24,90],"BE":[50.833333,4],"BF":[13,-2],"BG":[43,25],"BH":[26,50.5],"BI":[-3.5,30],"BJ":[9.5,2.25],"BL":[17.9,-62.833333],"BM":[32.333333,-64.75],"BN":[4.5,114.666667],"BO":[-17,-65],"BQ":[12.2,17.83333],"BR":[-10,-55],"BS":[24,-76],"BT":[27.5,90.5],"BV":[-54.433333,3.4],"BW":[-22,24],"BY":[53,28],"BZ":[17.25,-88.75],"CA":[60,-96],"CC":[-12,96.833333],"CD":[0,25],"CF":[7,21],"CG":[-1,15],"CH":[47,8],"CI":[8,-5],"CK":[-16.083333,-161.583333],"CL":[-30,-71],"CM":[6,12],"CN":[35,105],"CO":[4,-72],"CR":[10,-84],"CU":[22,-79.5],"CV":[16,-24],"CW":[12.166667,-69],"CX":[-10.5,105.666667],"CY":[35,33],"CZ":[49.75,15],"DE":[51.5,10.5],"DJ":[11.5,42.5],"DK":[56,10],"DM":[15.5,-61.333333],"DO":[19,-70.666667],"DZ":[28,3],"EC":[-2,-77.5],"EE":[59,26],"EG":[27,30],"EH":[25,-13.5],"ER":[15,39],"ES":[40,-4],"ET":[8,38],"EU":[48,10],"FI":[64,26],"FJ":[-18,178],"FK":[-51.75,-59.166667],"FM":[5,152],"FO":[62,-7],"FR":[46,2],"GA":[-1,11.75],"GB":[54,-4],"GD":[12.116667,-61.666667],"GE":[41.999981,43.499905],"GF":[4,-53],"GG":[49.583333,-2.333333],"GH":[8,-2],"GI":[36.133333,-5.35],"GL":[72,-40],"GM":[13.5,-15.5],"GN":[11,-10],"GP":[16.25,-61.583333],"GQ":[2,10],"GR":[39,22],"GS":[-56,-33],"GT":[15.5,-90.25],"GU":[13.4444444,144.7366667],"GW":[12,-15],"GY":[5,-59],"HK":[22.25,114.166667],"HM":[-53,73],"HN":[15,-86.5],"HR":[45.166667,15.5],"HT":[19,-72.416667],"HU":[47,20],"ID":[-5,120],"IE":[53,-8],"IL":[31.5,34.75],"IM":[54.25,-4.5],"IN":[20,77],"IO":[-6,72],"IQ":[33,44],"IR":[32,53],"IS":[65,-18],"IT":[42.833333,12.833333],"JE":[49.216667,-2.116667],"JM":[18.25,-77.5],"JO":[31,36],"JP":[36,138],"KE":[1,38],"KG":[41,75],"KH":[13,105],"KI":[-5,-170],"KM":[-12.166667,44.25],"KN":[17.333333,-62.75],"KP":[40,127],"KR":[37,127.5],"KW":[29.5,47.75],"KY":[19.5,-80.666667],"KZ":[48,68],"LA":[18,105],"LB":[33.833333,35.833333],"LC":[13.883333,-60.966667],"LI":[47.166667,9.533333],"LK":[7,81],"LR":[6.5,-9.5],"LS":[-29.5,28.25],"LT":[56,24],"LU":[49.75,6.166667],"LV":[57,25],"LY":[25,17],"MA":[32,-5],"MC":[43.733333,7.4],"MD":[47,29],"ME":[42.5,19.3],"MF":[18.075,-63.05833],"MG":[-20,47],"MH":[10,167],"MK":[41.833333,22],"ML":[17,-4],"MM":[22,98],"MN":[46,105],"MO":[22.157778,113.559722],"MP":[16,146],"MQ":[14.666667,-61],"MR":[20,-12],"MS":[16.75,-62.2],"MT":[35.916667,14.433333],"MU":[-20.3,57.583333],"MV":[3.2,73],"MW":[-13.5,34],"MX":[23,-102],"MY":[2.5,112.5],"MZ":[-18.25,35],"NA":[-22,17],"NC":[-21.5,165.5],"NE":[16,8],"NF":[-29.033333,167.95],"NG":[10,8],"NI":[13,-85],"NL":[52.5,5.75],"NO":[62,10],"NP":[28,84],"NR":[-0.533333,166.916667],"NU":[-19.033333,-169.866667],"NZ":[-42,174],"OM":[21,57],"PA":[9,-80],"PE":[-10,-76],"PF":[-15,-140],"PG":[-6,147],"PH":[13,122],"PK":[30,70],"PL":[52,20],"PM":[46.833333,-56.333333],"PN":[-25.066667,-130.1],"PR":[18.2482882,-66.4998941],"PS":[31.666667,35.25],"PT":[39.5,-8],"PW":[6,134],"PY":[-22.993333,-57.996389],"QA":[25.5,51.25],"RE":[-21.1,55.6],"RO":[46,25],"RS":[44,21],"RU":[60,100],"RW":[-2,30],"SA":[25,45],"SB":[-8,159],"SC":[-4.583333,55.666667],"SD":[16,30],"SE":[62,15],"SG":[1.366667,103.8],"SH":[-15.95,-5.7],"SI":[46.25,15.166667],"SJ":[78,20],"SK":[48.666667,19.5],"SL":[8.5,-11.5],"SM":[43.933333,12.416667],"SN":[14,-14],"SO":[6,48],"SR":[4,-56],"SS":[8,30],"ST":[1,7],"SV":[13.833333,-88.916667],"SX":[18.04167,-63.06667],"SY":[35,38],"SZ":[-26.5,31.5],"TC":[21.733333,-71.583333],"TD":[15,19],"TF":[-43,67],"TG":[8,1.166667],"TH":[15,100],"TJ":[39,71],"TK":[-9,-171.75],"TL":[-8.833333,125.75],"TM":[40,60],"TN":[34,9],"TO":[-20,-175],"TR":[39.059012,34.911546],"TT":[11,-61],"TV":[-8,178],"TW":[24,121],"TZ":[-6,35],"UA":[49,32],"UG":[2,33],"UM":[5.8811111,-162.0725],"US":[39.828175,-98.5795],"UY":[-33,-56],"UZ":[41.707542,63.84911],"VA":[41.9,12.45],"VC":[13.083333,-61.2],"VE":[8,-66],"VG":[18.5,-64.5],"VI":[18.3482891,-64.9834807],"VN":[16.166667,107.833333],"VU":[-16,167],"WF":[-13.3,-176.2],"WS":[-13.803096,-172.178309],"XK":[42.58333,21],"YE":[15.5,47.5],"YT":[-12.833333,45.166667],"ZA":[-30,26],"ZM":[-15,30],"ZW":[-19,29],"AP":[115,9.5]}
# country names
cc_names    = {"AD":"Andorra","AE":"United Arab Emirates","AF":"Afghanistan","AG":"Antigua and Barbuda","AI":"Anguilla","AL":"Albania","AM":"Armenia","AN":"Netherlands Antilles","AO":"Angola","AQ":"Antarctica","AR":"Argentina","AS":"American Samoa","AT":"Austria","AU":"Australia","AW":"Aruba","AX":"ALA Aland Islands","AZ":"Azerbaijan","BA":"Bosnia and Herzegovina","BB":"Barbados","BD":"Bangladesh","BE":"Belgium","BF":"Burkina Faso","BG":"Bulgaria","BH":"Bahrain","BI":"Burundi","BJ":"Benin","BL":"Saint-Barthélemy","BM":"Bermuda","BN":"Brunei Darussalam","BO":"Bolivia","BQ":"Bonaire","BR":"Brazil","BS":"Bahamas","BT":"Bhutan","BV":"Bouvet Island","BW":"Botswana","BY":"Belarus","BZ":"Belize","CA":"Canada","CC":"Cocos (Keeling) Islands","CD":"Congo, (Kinshasa)","CF":"Central African Republic","CG":"Congo (Brazzaville)","CH":"Switzerland","CI":"Côte d'Ivoire","CK":"Cook Islands","CL":"Chile","CM":"Cameroon","CN":"China","CO":"Colombia","CR":"Costa Rica","CU":"Cuba","CV":"Cape Verde","CW":"Curaçao","CX":"Christmas Island","CY":"Cyprus","CZ":"Czech Republic","DE":"Germany","DJ":"Djibouti","DK":"Denmark","DM":"Dominica","DO":"Dominican Republic","DZ":"Algeria","EC":"Ecuador","EE":"Estonia","EG":"Egypt","EH":"Western Sahara","ER":"Eritrea","ES":"Spain","ET":"Ethiopia","EU":"Europe","FI":"Finland","FJ":"Fiji","FK":"Falkland Islands (Malvinas)","FM":"Micronesia, Federated States of","FO":"Faroe Islands","FR":"France","GA":"Gabon","GB":"United Kingdom","GD":"Grenada","GE":"Georgia","GF":"French Guiana","GG":"Guernsey","GH":"Ghana","GI":"Gibraltar","GL":"Greenland","GM":"Gambia","GN":"Guinea","GP":"Guadeloupe","GQ":"Equatorial Guinea","GR":"Greece","GS":"South Georgia and the South Sandwich Islands","GT":"Guatemala","GU":"Guam","GW":"Guinea-Bissau","GY":"Guyana","HK":"Hong Kong, SAR China","HM":"Heard and Mcdonald Islands","HN":"Honduras","HR":"Croatia","HT":"Haiti","HU":"Hungary","ID":"Indonesia","IE":"Ireland","IL":"Israel","IM":"Isle of Man","IN":"India","IO":"British Indian Ocean Territory","IQ":"Iraq","IR":"Iran, Islamic Republic of","IS":"Iceland","IT":"Italy","JE":"Jersey","JM":"Jamaica","JO":"Jordan","JP":"Japan","KE":"Kenya","KG":"Kyrgyzstan","KH":"Cambodia","KI":"Kiribati","KM":"Comoros","KN":"Saint Kitts and Nevis","KP":"Korea (North)","KR":"Korea (South)","KW":"Kuwait","KY":"Cayman Islands","KZ":"Kazakhstan","LA":"Lao PDR","LB":"Lebanon","LC":"Saint Lucia","LI":"Liechtenstein","LK":"Sri Lanka","LR":"Liberia","LS":"Lesotho","LT":"Lithuania","LU":"Luxembourg","LV":"Latvia","LY":"Libya","MA":"Morocco","MC":"Monaco","MD":"Moldova","ME":"Montenegro","MF":"Saint-Martin (French part)","MG":"Madagascar","MH":"Marshall Islands","MK":"Macedonia, Republic of","ML":"Mali","MM":"Myanmar","MN":"Mongolia","MO":"Macao, SAR China","MP":"Northern Mariana Islands","MQ":"Martinique","MR":"Mauritania","MS":"Montserrat","MT":"Malta","MU":"Mauritius","MV":"Maldives","MW":"Malawi","MX":"Mexico","MY":"Malaysia","MZ":"Mozambique","NA":"Namibia","NC":"New Caledonia","NE":"Niger","NF":"Norfolk Island","NG":"Nigeria","NI":"Nicaragua","NL":"Netherlands","NO":"Norway","NP":"Nepal","NR":"Nauru","NU":"Niue","NZ":"New Zealand","OM":"Oman","PA":"Panama","PE":"Peru","PF":"French Polynesia","PG":"Papua New Guinea","PH":"Philippines","PK":"Pakistan","PL":"Poland","PM":"Saint Pierre and Miquelon","PN":"Pitcairn","PR":"Puerto Rico","PS":"Palestinian Territory","PT":"Portugal","PW":"Palau","PY":"Paraguay","QA":"Qatar","RE":"Réunion","RO":"Romania","RS":"Serbia","RU":"Russian Federation","RW":"Rwanda","SA":"Saudi Arabia","SB":"Solomon Islands","SC":"Seychelles","SD":"Sudan","SE":"Sweden","SG":"Singapore","SH":"Saint Helena","SI":"Slovenia","SJ":"Svalbard and Jan Mayen Islands","SK":"Slovakia","SL":"Sierra Leone","SM":"San Marino","SN":"Senegal","SO":"Somalia","SR":"Suriname","SS":"South Sudan","ST":"Sao Tome and Principe","SV":"El Salvador","SX":"Sint Maarten","SY":"Syrian Arab Republic","SZ":"Swaziland","TC":"Turks and Caicos Islands","TD":"Chad","TF":"French Southern Territories","TG":"Togo","TH":"Thailand","TJ":"Tajikistan","TK":"Tokelau","TL":"Timor-Leste","TM":"Turkmenistan","TN":"Tunisia","TO":"Tonga","TR":"Turkey","TT":"Trinidad and Tobago","TV":"Tuvalu","TW":"Taiwan, Republic of China","TZ":"Tanzania, United Republic of","UA":"Ukraine","UG":"Uganda","UM":"US Minor Outlying Islands","US":"United States of America","UY":"Uruguay","UZ":"Uzbekistan","VA":"Holy See (Vatican City State)","VC":"Saint Vincent and Grenadines","VE":"Venezuela","VG":"British Virgin Islands","VI":"Virgin Islands, US","VN":"Viet Nam","VU":"Vanuatu","WF":"Wallis and Futuna Islands","WS":"Samoa","XK":"Kosovo","YE":"Yemen","YT":"Mayotte","ZA":"South Africa","ZM":"Zambia","ZW":"Zimbabwe","AP":"Asia/Pacific Region"}

# =========================================================================== #
# load peering db into memory
# =========================================================================== #

def pdb_load():
    ''' load all peering_db database into memory '''
    con = sqlite3.connect('data-raw/peeringdb.sqlite3')
    con.row_factory = sqlite3.Row
    cursor = con.cursor()

    tables = [
        'peeringdb_organization',
        'peeringdb_facility',
        'peeringdb_network',
        'peeringdb_ix',
        'peeringdb_ix_facility',
        'peeringdb_ixlan',
        'peeringdb_ixlan_prefix',
        'peeringdb_network_contact',
        'peeringdb_network_facility',
        'peeringdb_network_ixlan',
    ]

    data = {}

    # print '> loading peering db'
    for tab in tables:
        cursor.execute("SELECT * FROM %s" % tab)

        db = {}

        for r in cursor.fetchall():
            obj = { k: r[k] for k in r.keys() }
            if obj['status'] == 'deleted':
                continue
            db[obj['id']] = obj

        tabname = tab.replace('peeringdb_', '')
        data[tabname] = db
        # print '> loaded %s db %d items' % (tabname, len(db))

    # print '> done.'
    return data


# =========================================================================== #
# merge all sources of data for each net
# =========================================================================== #
asn2net = {}
def net_load(asn, nics, pdb, bgp):
    ''' returns dict for specified ASn with all sources of info '''
    asn = str(asn)
    asi = int(asn)

    # make lookup table for ASN -> peering_db net obj
    global asn2net
    if not len(asn2net):
        asn2net = { pdb['network'][i]['asn']: pdb['network'][i] for i in pdb['network'] }

    # get objs from all our dbs
    net_nic = nics['asn'][asn]      if asn in nics['asn']   else None
    net_pdb = asn2net[asi]          if asi in asn2net       else None
    net_bgp = bgp[asn]              if asn in bgp           else None

    net = {
        # basic info
        'asn':          asi,
        'cc':           net_nic['cc'],
        'registry':     net_nic['registry'],
        'name':         net_pdb['name']             if net_pdb else '',
        'type':         net_pdb['info_type']        if net_pdb else '',
        'website':      net_pdb['website']          if net_pdb else '',

        # prefixes
        'prefix':       net_bgp['prefix']           if net_bgp else [],
        'prefix4':      net_bgp['prefix4']          if net_bgp else 0,
        'prefix6':      net_bgp['prefix6']          if net_bgp else 0,
        'addr4':        0,
        'addr6':        0,

        # calculated speed (minimal) & announced total speed
        'speed_ix':     0,
        'speed_tot':    net_pdb['info_traffic']     if net_pdb else 0,

        # links (most are enriched later)
        'links_as':     net_bgp['links']            if net_bgp else [],
        'links_dir':    {},                         # dict[CC]: { 'net': [], 'fac':[], 'ix':[] }
        'links_ind':    {},                         # dict[CC]: { 'net': [], 'fac':[], 'ix':[] }
        'fac_ids':      [],                         # list of fac id
        'ix_ids':       [],                         # list of ix id
        'ix_speed':     {},                         # dict[ix_id]: link_speed
    }

    if not len(net['cc']):
        net['cc'] = '??'

    lst_pfx         = [ netaddr.IPNetwork(pfx) for pfx in net['prefix'] ]
    lst_pfx_merged  = netaddr.cidr_merge(lst_pfx)
    net['prefix']   = [ str(_) for _ in lst_pfx_merged ]
    net['prefix4']  = 0
    net['prefix6']  = 0
    for pfx in net['prefix']:
        slash = int(pfx[pfx.find('/')+1:])
        if ':' in pfx:
            net['addr6'] += 1 << (128 - slash)
            net['prefix6'] += 1
        else:
            net['addr4'] += 1 << (32 - slash)
            net['prefix4'] += 1

    if not len(net['name']) and asn in db_names:
        net['name'] = db_names[asn]

    return net


# =========================================================================== #
# enrich nets with more info from peering_db
# =========================================================================== #
def net_enrich(nets, pdb):

    # add list of private facilities to each network
    for i in pdb['network_facility']:
        obj = pdb['network_facility'][i]
        nid = pdb['network_facility'][i]['net_id']
        net = pdb['network'][nid]
        asn = str(net['asn'])
        if not asn in nets:
            # print '> bad AS %s' % asn
            continue
        if not obj['fac_id'] in nets[asn]['fac_ids']:
            nets[asn]['fac_ids'].append(obj['fac_id'])

    # add ix to each network + speed
    for i in pdb['network_ixlan']:
        obj = pdb['network_ixlan'][i]
        nid = pdb['network_ixlan'][i]['net_id']
        net = pdb['network'][nid]
        asn = str(net['asn'])
        spd = obj['speed']
        xid = pdb['ixlan'][obj['ixlan_id']]['ix_id']

        if not asn in nets:
            # print '> bad AS %s' % asn
            continue
        if xid not in nets[asn]['ix_ids']:
            nets[asn]['ix_ids'].append(xid)
        if xid not in nets[asn]['ix_speed']:
            nets[asn]['ix_speed'][xid] = spd
        else:
            nets[asn]['ix_speed'][xid] += spd

        nets[asn]['speed_ix']   += spd

    # build list of indirect & direct CC links for each net
    for asn in nets:
        net = nets[asn]

        # linked to cc because of direct link to ix
        for xid in net['ix_ids']:
            cc = pdb['ix'][xid]['country']
            _add_link(net, cc, 'links_dir', 'ix', xid)

        # linked to cc because of direct link to facility
        for fid in net['fac_ids']:
            cc = pdb['facility'][fid]['country']
            _add_link(net, cc, 'links_dir', 'fac', fid)

        # indirect links to cc because of direct link to AS
        for lasn in net['links_as']:
            if not str(lasn) in nets:
                continue
            _add_link(net, nets[str(lasn)]['cc'], 'links_ind', 'net', lasn)

    # sort lists
    for asn in nets:
        net['links_as']     = sorted(net['links_as'])
        net['fac_ids']      = sorted(net['fac_ids'])
        net['ix_ids']       = sorted(net['ix_ids'])


# =========================================================================== #
# enrich facilities
# =========================================================================== #
def facs_enrich(db_pdb):
    path_geofac = 'data/geofacs.json'

    # load our facility coords database
    geofacs = wnm_load(path_geofac, [])

    # look it up for this fac
    for gf in geofacs:
        i   = int(gf['idfac'])
        if not i in db_pdb['facility']:
            continue
        if not 'lat' in gf or not 'lng' in gf:
            continue
        db_pdb['facility'][i]['lat'] = gf['lat']
        db_pdb['facility'][i]['lng'] = gf['lng']

    # resolve missing coords
    for i in db_pdb['facility']:
        # no coords for this facility yet?
        if not 'lat' in db_pdb['facility'][i] or not 'lng' in db_pdb['facility'][i]:
            f = db_pdb['facility'][i]
            # build a geoloc request
            q = '%s,%s,%s,%s,%s,%s' % ( f['address1'], f['address2'], f['zipcode'], f['city'], f['state'], f['country'] )
            q = unicode(q).encode('utf-8')

            try:
                f['lat'], f['lng'] = geo_lookup(q)
                geofacs.append({ 'idfac': i, 'lat': f['lat'], 'lng': f['lng'] })
            except:
                # print '> geo fail for %d %s (%s)' % (i, f['name'].encode('utf-8'), q)
                f['lat'], f['lng'] = 0, 0

        # initialize var for list of nets & ixes
        db_pdb['facility'][i]['citydist']   = 0
        db_pdb['facility'][i]['citycoords'] = [0, 0]
        db_pdb['facility'][i]['nets']   = []     # list of asn
        db_pdb['facility'][i]['ix']     = []       # list of ixid


    # add list ASN to each facility
    for i in db_pdb['network_facility']:
        fid = db_pdb['network_facility'][i]['fac_id']
        nid = db_pdb['network_facility'][i]['net_id']
        net = db_pdb['network'][nid]
        if not str(net['asn']) in nets:
            continue
        if not net['asn'] in db_pdb['facility'][fid]['nets']:
            db_pdb['facility'][fid]['nets'].append(net['asn'])

    # add list of IX to each facility
    for i in db_pdb['ix_facility']:
        fid = db_pdb['ix_facility'][i]['fac_id']
        xid = db_pdb['ix_facility'][i]['ix_id']
        if not xid in db_pdb['facility'][fid]['ix']:
            db_pdb['facility'][fid]['ix'].append(xid)

    # sort list of nets & ix
    for i in db_pdb['facility']:
        db_pdb['facility'][i]['nets']   = sorted(db_pdb['facility'][i]['nets'])
        db_pdb['facility'][i]['ix']     = sorted(db_pdb['facility'][i]['ix'])

    # lookup city coords..
    n, t = 0, len(db_pdb['facility'])
    for i in db_pdb['facility']:
        cc = db_pdb['facility'][i]['country']
        ct = db_pdb['facility'][i]['city'].lower()
        st = db_pdb['facility'][i]['state'].upper()

        co = find_city(cc, st, ct)
        if co:
            db_pdb['facility'][i]['citydist']   = gps_dist(db_pdb['facility'][i]['lat'], db_pdb['facility'][i]['lng'], co[0], co[1])
            db_pdb['facility'][i]['citycoords'] = [ float(co[0]), float(co[1]) ]

    # rewrite our database of facid -> gps coords
    wnm_save(path_geofac, geofacs)

def find_city(cc, state, name):
    if cc not in db_cities:
        return None

    def _to_unicode(s):
        try:
            return unicode(s)
        except:
            pass
        try:
            return unicode(s.decode('utf-8'))
        except:
            return unicode(s.decode('latin-1'))

    def _fix(s):
        while s.find('  ') >= 0:
            s = s.replace('  ', ' ')
        s = s.strip()
        s = s.lower()
        s = s.replace(' ', '-')
        return s

    # damn us of a
    if cc == 'US':
        name = '%s-%s' % (state, name)

    # fix name & first attempt
    n = _fix(name)
    if n in db_cities[cc]:
        return db_cities[cc][n]

    # unidecode
    u = _to_unicode(n)
    n = unidecode.unidecode(u).encode('utf-8')
    if n in db_cities[cc]:
        return db_cities[cc][n]

    # fix abreviations
    if name[0:3] == 'st.':
        n = _fix('saint ' + name[3:])
        if n in db_cities[cc]:
            return db_cities[cc][n]
    if name[0:3] == 'ft.':
        n = _fix('fort ' + name[3:])
        if n in db_cities[cc]:
            return db_cities[cc][n]

    # parenthesis
    if '(' in name and ')' in name:
        # try what is inside the parenthesis
        n = _fix(name[ name.find('(') + 1: name.find(')')])
        if n in db_cities[cc]:
            return db_cities[cc][n]
        # try what is outside the parenthesis
        n = _fix(name[ 0: name.find('(') ])
        if n in db_cities[cc]:
            return db_cities[cc][n]

    # slashes & dashes
    for split in ['/', '-']:
        if split in name:
            for i in range(2):
                n = _fix(name.split(split)[i])
                if n in db_cities[cc]:
                    return db_cities[cc][n]

    # still not found :(
    # last ditch effort
    for n in name.split(' '):
        n = _fix(n)
        if n in db_cities[cc]:
            return db_cities[cc][n]

    return None

# =========================================================================== #
# enrich facilities
# =========================================================================== #
def ix_enrich(db_pdb):
    for i in db_pdb['ix']:
        db_pdb['ix'][i]['facilities']  = []
        db_pdb['ix'][i]['nets']        = []
        db_pdb['ix'][i]['speeds']      = {}
        db_pdb['ix'][i]['bandwith']    = 0

    # ASN + speed to each ix
    for i in db_pdb['network_ixlan']:
        obj = db_pdb['network_ixlan'][i]
        nid = db_pdb['network_ixlan'][i]['net_id']
        net = db_pdb['network'][nid]
        spd = obj['speed']
        asn = str(net['asn'])
        xid = db_pdb['ixlan'][obj['ixlan_id']]['ix_id']
        if not asn in nets:
            continue
        if not asn in db_pdb['ix'][xid]['nets']:
            db_pdb['ix'][xid]['nets'].append(asn)
        if asn not in db_pdb['ix'][xid]['speeds']:
            db_pdb['ix'][xid]['speeds'][asn] = spd
        else:
            db_pdb['ix'][xid]['speeds'][asn] += spd
        db_pdb['ix'][xid]['bandwith'] += spd

    # add facilities to each ix
    for i in db_pdb['ix_facility']:
        fid = db_pdb['ix_facility'][i]['fac_id']
        xid = db_pdb['ix_facility'][i]['ix_id']
        if not fid in db_pdb['ix'][xid]['facilities']:
            db_pdb['ix'][xid]['facilities'].append(fid)

    # sort data
    for i in db_pdb['ix']:
        db_pdb['ix'][i]['facilities']  = sorted(db_pdb['ix'][i]['facilities'])
        db_pdb['ix'][i]['nets']        = sorted(db_pdb['ix'][i]['nets'])

# =========================================================================== #
# make some stats about countries
# =========================================================================== #
def country_stats(nets, pdb, scdb, world):
    countries =         { nets[asn]['cc']:               {} for asn in nets             if len(nets[asn]['cc']) }
    countries.update(   { pdb['ix'][i]['country']:       {} for i in pdb['ix']          if len(pdb['ix'][i]['country'])  } )
    countries.update(   { pdb['facility'][i]['country']: {} for i in pdb['facility']    if len(pdb['facility'][i]['country'])  } )
    countries.update(   { cc:                            {} for cc in scdb['countries'] } )

    for cc in countries:
        countries[cc]['cc']             = cc
        countries[cc]['iso3']           = iso3[cc]      if(cc != '??')                else '???'
        countries[cc]['center']         = cc_gps[cc]    if(cc != '??')                else [0, 0]
        countries[cc]['name']           = cc_names[cc]  if(cc != '??')                else "Unknown"
        countries[cc]['num_ix']         = 0
        countries[cc]['ix_ids']         = []
        countries[cc]['num_fac']        = 0
        countries[cc]['fac_ids']        = []
        countries[cc]['num_net']        = 0
        countries[cc]['prefix4']        = 0
        countries[cc]['prefix6']        = 0
        countries[cc]['addr4']          = 0
        countries[cc]['addr6']          = 0
        countries[cc]['nets_ext']       = []
        countries[cc]['nets_loc']       = [] # asn
        countries[cc]['links_dir_inc']  = {} # dict[cc] = { 'net': [], 'fac': [], 'ix': [] }
        countries[cc]['links_dir_out']  = {} # dict[cc] = { 'net': [], 'fac': [], 'ix': [] }
        countries[cc]['links_ind_inc']  = {} # dict[cc] = { 'net': [], 'fac': [], 'ix': [] }
        countries[cc]['links_ind_out']  = {} # dict[cc] = { 'net': [], 'fac': [], 'ix': [] }
        countries[cc]['landings']       = []
        countries[cc]['cables']         = []
        countries[cc]['lnd']            = float(world[cc]['Area(in sq km)'])    if (cc != '??' and cc != 'EU' and cc != 'AP') else 0
        countries[cc]['pop']            = float(world[cc]['Population'])        if (cc != '??' and cc != 'EU' and cc != 'AP') else 0
        countries[cc]['info']           = world[cc]                             if (cc != '??' and cc != 'EU' and cc != 'AP') else {}

    # country stats: num of ix
    for i in pdb['ix']:
        ix = pdb['ix'][i]
        cc = ix['country']
        countries[cc]['num_ix'] += 1
        countries[cc]['ix_ids'].append(i)

    # country stats: num of facs
    for i in pdb['facility']:
        fac = pdb['facility'][i]
        cc  = fac['country']
        if not len(cc):
            print fac
            continue
        countries[cc]['num_fac'] += 1
        countries[cc]['fac_ids'].append(i)

    # country stats: num of nets, ext_nets, local_nets & ipv4/ipv6 prefix num
    for asn in nets:
        net = nets[asn]
        cc  = net['cc']
        countries[cc]['num_net'] += 1
        countries[cc]['prefix4'] += net['prefix4']
        countries[cc]['prefix6'] += net['prefix6']
        countries[cc]['addr4']   += net['addr4']
        countries[cc]['addr6']   += net['addr6']
        countries[cc]['nets_loc']+= [ net['asn'] ]

        # country links from / to this network
        for cat in ['links_dir', 'links_ind']:
            for lcc in net[cat]:
                _add_link(countries[cc], lcc, cat + '_out', 'net', net['asn'])
                _add_link(countries[lcc], cc, cat + '_inc', 'net', net['asn'])
                if cat == 'links_dir' and net['cc'] not in countries[lcc]['nets_ext']:
                    countries[lcc]['nets_ext'].append(net['asn'])

    # add submarine cable info
    for cc in scdb['countries']:
        countries[cc]['landings']   = scdb['countries'][cc]['landings']
        countries[cc]['cables']     = scdb['countries'][cc]['cables']

        # country links from / to this cable
        for cid in countries[cc]['cables']:
            for lcc in scdb['cables'][cid]['countries']:
                _add_link(countries[cc], lcc, 'links_dir_out', 'cable', cid)
                _add_link(countries[cc], lcc, 'links_dir_inc', 'cable', cid)


    # sort lists
    for cc in countries:
        countries[cc]['nets_ext'] = sorted(countries[cc]['nets_ext'])
        countries[cc]['nets_loc'] = sorted(countries[cc]['nets_loc'])
        countries[cc]['ix_ids']   = sorted(countries[cc]['ix_ids'])
        countries[cc]['fac_ids']  = sorted(countries[cc]['fac_ids'])


    return countries

# =========================================================================== #
# enrich utilities
# =========================================================================== #

# store a link to a country (incoming or outgoing) via net / fac / ix
def _add_link(obj, cc, subcat, typ, val):
    # ignore links to home country
    if cc == obj['cc']:
        return

    # direct or indirect?
    if not cc in obj[subcat]:
        obj[subcat][cc] = {}
    root = obj[subcat][cc]

    # store it now
    if typ not in root:
        root[typ] = []
    if not val in root[typ]:
        root[typ].append(val)

def gps_dist(lat1, lng1, lat2, lng2):
    # change base from [-180, 180] to [0, 360]
    lat1 = float(lat1) + 180
    lat2 = float(lat2) + 180
    # change base from [-90, 90] to [0, 180]
    lng1 = float(lng1) + 90
    lng2 = float(lng2) + 90

    return math.sqrt(pow(lat2 - lat1, 2) + pow(lng2 - lng1, 2))

# =========================================================================== #
# main
# =========================================================================== #

print '========================================'
print '> Merging databases'
print '========================================'

db_nics     = wnm_load('data/nics.json')
db_bgp      = wnm_load('data/bgp.json')
db_scdb     = wnm_load('data/scdb.json')
db_names    = wnm_load('data/asnames.json')
db_cities   = wnm_load('data/cities.json')
db_world    = wnm_load('data/worldinfo.json')

print '> loading peering db ..'
db_pdb      = pdb_load()

print '> merging network info ..'
nets        = { asn: net_load(asn, db_nics, db_pdb, db_bgp) for asn in db_nics['asn'] }

print '> enriching networks ..'
net_enrich(nets, db_pdb)

print '> enriching facilities ..'
facs_enrich(db_pdb)

print '> enriching IXs ..'
ix_enrich(db_pdb)

print '> building country stats ..'
countries = country_stats(nets, db_pdb, db_scdb, db_world)

# final database
final = {
    'nets':         nets,
    'countries':    countries,
    'facilities':   db_pdb['facility'],
    'ixs':          db_pdb['ix'],
    'cables':       db_scdb['cables'],
    'landings':     db_scdb['landings'],
}
wnm_save('data/final.json', final)

sys.exit(0)

