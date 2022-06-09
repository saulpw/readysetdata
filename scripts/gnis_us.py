#!/usr/bin/env python

from dxd.utils import require_file, unzip, output, asv


def main():
    data = unzip(require_file('https://geonames.usgs.gov/docs/stategaz/NationalFile.zip'))

    import zipfile
    with zipfile.Path(data, data.namelist()[0]).open() as fp:
        output('gnis', 'us', (
            dict(
#                feature_id = r.FEATURE_ID,
                name = r.FEATURE_NAME,
                type = r.FEATURE_CLASS,
                state = r.STATE_ALPHA,
                county = r.COUNTY_NAME,
                lat = float(r.PRIM_LAT_DEC),
                long = float(r.PRIM_LONG_DEC),
                elev_m = int(r.ELEV_IN_M) if r.ELEV_IN_M else None,
            ) for r in asv(fp, '|')
        ))

main()
