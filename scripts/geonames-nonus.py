#!/usr/bin/env python3

from readysetdata import parse_asv, download, output, unzip_text

URL = 'https://geonames.nga.mil/gns/html/cntyfile/geonames_20220606.zip'

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

output('geonames', 'non_us', 'name feat_class lat:f long:f lang country_code note pop_class:i',
        ((
         r.SHORT_FORM or r.FULL_NAME_RO,
         FC_map.get(r.FC, r.FC),  # feature class
         float(r.LAT) if r.LAT else None,
         float(r.LONG) if r.LONG else None,
         r.LC,
         r.CC1,
         r.NOTE,
         int(r.PC) if r.PC else None,
        ) for r in parse_asv(unzip_text(download(URL), 'Countries.txt'))))
