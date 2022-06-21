#!/usr/bin/env python

from dxd.utils import download, unzip, output, asv


def main():
    data = unzip(download('https://geonames.usgs.gov/docs/stategaz/NationalFile.zip'))

    import zipfile
    with zipfile.Path(data, data.namelist()[0]).open() as fp:
        output('geonames', 'us', 'name type state county lat:f long:f elev_m:i', ((
#            r.FEATURE_ID,
            r.FEATURE_NAME,
            r.FEATURE_CLASS,
            r.STATE_ALPHA,
            r.COUNTY_NAME,
            float(r.PRIM_LAT_DEC),
            float(r.PRIM_LONG_DEC),
            int(r.ELEV_IN_M) if r.ELEV_IN_M and r.ELEV_IN_FT != -1000001 else None
        ) for r in asv(fp, '|')))


main()
