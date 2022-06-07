import sys


class JsonLines:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        import json

        for i, line in enumerate(self.fp):
            if i % 100000 == 0:
                print(f'\r{self.fp.name} {i}', end='', file=sys.stderr)
                sys.stderr.flush()
            yield json.loads(line)

        print('', file=sys.stderr)


def output_parquet(dbname, tblname, rows, fields=None):
    import pyarrow as pa
    import pyarrow.parquet as pq

    if not fields:
        fields = list(rows[0].keys())

    pq.write_table(pa.table(
            [ [r.get(fieldname, None) for r in rows] for fieldname in fields],
            names=fields),
            f'{dbname}_{tblname}.parquet')


def output_duckdb(dbname, tblname, rows, fields=None):
    import pyarrow as pa
    import duckdb

    if not fields:
        fields = list(rows[0].keys())

    tbl = pa.table(
            [ [r.get(fieldname, None) for r in rows] for fieldname in fields],
            names=fields)

    con = duckdb.connect(f'{dbname}.duckdb')
    con.execute(f"CREATE TABLE {tblname} AS SELECT * FROM tbl")



def require_file(urlstr:str):
    from urllib.parse import urlparse
    from pathlib import Path

    url = urlparse(urlstr)

    p = Path(url.netloc, *Path(url.path[1:]).parts)

    if not p.exists():
        parentdir = Path(url.netloc, *Path(url.path[1:]).parent.parts)
        parentdir.mkdir(parents=True, exist_ok=True)

        with p.open(mode='wb') as fp:
            import requests
            resp = requests.get(url)
            fp.write(resp.raw)

    return p


def unzip(p):
    import zipfile
    return zipfile.ZipFile(p)
