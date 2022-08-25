#!/usr/bin/env python3

from readysetdata import parse_asv, output, unzip_url

URL = 'https://geonames.nga.mil/gns/html/cntyfile/geonames_20220606.zip'
# https://geonames.nga.mil/geonames/GNSData/fc_files/Whole_World.7z
# URL and structure of zip have changed

FC_map = dict(
    A = 'Administrative region',
    P = 'Populated place',
    V = 'Vegetation',
    L = 'Locality or area',
    U = 'Undersea',
    R = 'Streets, highways, roads, or railroad',
    T = 'Hypsographic',
    H = 'Hydrographic',
    S = 'Spot',
)

output('geonames', 'non_us',
        ({
            'name': r.SHORT_FORM or r.FULL_NAME_RO,
            'feat_class': FC_map.get(r.FC, r.FC),  # feature class
            'lat:f': float(r.LAT) if r.LAT else None,
            'long:f': float(r.LONG) if r.LONG else None,
            'lang': r.LC,
            'country_code': r.CC1,
            'note': r.NOTE,
            'pop_class:b': int(r.PC) if r.PC else None,
        } for r in parse_asv(unzip_url(URL).open_text('Countries.txt'))))
