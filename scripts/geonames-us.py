#!/usr/bin/env python3

import zipfile

from readydata import download, unzip, output, parse_asv

URL = 'https://geonames.usgs.gov/docs/stategaz/NationalFile.zip'

data = unzip(download(URL))

with zipfile.Path(data, data.namelist()[0]).open() as fp:
    output('geonames', 'us', ({
#        'feature_id': r.FEATURE_ID,
        'name': r.FEATURE_NAME,
        'type': r.FEATURE_CLASS,
        'state': r.STATE_ALPHA,
        'county': r.COUNTY_NAME,
        'lat:f': float(r.PRIM_LAT_DEC),
        'long:f': float(r.PRIM_LONG_DEC),
        'elev_m:i': int(r.ELEV_IN_M) if r.ELEV_IN_M and r.ELEV_IN_FT != -1000001 else None
    } for r in parse_asv(fp, '|')))
