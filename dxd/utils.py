import sys
import itertools
from pathlib import Path

debug = '--debug' in sys.argv


class AttrDict(dict):
    'Augment a dict with more convenient .attr syntax.  not-present keys return None.'
    def __getattr__(self, k):
        try:
            v = self[k]
            if isinstance(v, dict) and not isinstance(v, AttrDict):
                v = AttrDict(v)
            return v
        except KeyError:
            if k.startswith("__"):
                raise AttributeError
            return None


def asv(fp, delim='\t'):
    it = iter(fp)
    hdrs = next(it).split(delim)

    import sys
    for i, line in enumerate(it):
        yield AttrDict(zip(hdrs, line.split('|')))
        if i % 10000 == 0:
            print(f'\r{fp.name} {i}', end='', file=sys.stderr)
            sys.stderr.flush()
            if debug and i:
                break

    print('', file=sys.stderr)


class JsonLines:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        import json

        for i, line in enumerate(self.fp):
            if i % 10000 == 0:
                print(f'\r{self.fp.name} {i}', end='', file=sys.stderr)
                sys.stderr.flush()
                if debug and i:
                    break
            yield json.loads(line)

        print('', file=sys.stderr)


def pyarrow_table(rows, fields=None, types=None):
    import pyarrow as pa

    rows = list(rows)
    if not fields:
        fields = list(rows[0].keys())

    return pa.table([ [r.get(fieldname, None) for r in rows] for fieldname in fields],
            names=fields)


def get_optarg(arg):
    try:
        i = sys.argv.index(arg)
        return sys.argv[i+1]
    except ValueError:
        return ''


def output(dbname, tblname, rows, **kwargs):
    fmtstr = get_optarg('-f')

    if fmtstr:
        fmts = fmtstr.split(',')
    else:
        fmts = [func.removeprefix('output_')
                  for func in globals()
                    if func.startswith('output_')]

    outdir = get_optarg('-o') or '.'
    Path(outdir).mkdir(parents=True, exist_ok=True)

    rows = list(rows)  # in case of iterator, listify once and for all

    for fmt in fmts:
        if fmt:
            globals()[f'output_{fmt}'](str(Path(outdir)/dbname), tblname, rows, **kwargs)


def output_parquet(dbname, tblname, rows, fields=None):
    import pyarrow.parquet as pq

    pq.write_table(pyarrow_table(rows, fields), f'{dbname}_{tblname}.parquet')


def output_duckdb(dbname, tblname, rows, fields=None):
    import duckdb

    tbl = pyarrow_table(rows, fields)

    con = duckdb.connect(f'{dbname}.duckdb')
    con.execute(f"CREATE TABLE {tblname} AS SELECT * FROM tbl")


def pyarrow_arrays(rows, fields=None, types=None):
    import pyarrow as pa
    typemap = {
        'f': pa.float32(),
        'd': pa.float64(),
        'i': pa.int32(),
        'l': pa.int64(),
    }

    schema = pa.schema([
        (fieldname, typemap.get(type, pa.string()))
            for fieldname, type in zip(fields, types)]
    )

    return [
        pa.array([r.get(fieldname, None) for r in rows], type=typemap.get(type, None))
            for fieldname, type in itertools.zip_longest(fields, types)
    ]


def output_arrow(dbname, tblname, rows, fields=None, types='', new_writer=None):
    import pyarrow as pa

    typemap = {
        'f': pa.float32(),
        'd': pa.float64(),
        'i': pa.int32(),
        'l': pa.int64(),
    }

    def gettype(v):
        if isinstance(v, list):
            return pa.list_(gettype(v[0]))

        type_typemap = {
            int: pa.int64(),
            float: pa.float64(),
            str: pa.string(),
        }
        return type_typemap.get(type(v))


    rows = list(rows)
    if not fields:
        firstrow = rows[0]
        fields = list(firstrow.keys())
        types = [
            gettype(f) for f in firstrow.values()
        ]

    schema = pa.schema([
        (fieldname, typemap.get(type, type))
            for fieldname, type in zip(fields, types)]
    )

    if not new_writer:
        new_writer = pa.ipc.new_file
    with open(f'{dbname}_{tblname}.arrow', mode='wb') as outf:
        with new_writer(outf, schema) as writer:
            writer.write_batch(pa.record_batch(pyarrow_arrays(rows, fields, types), names=fields))


def output_arrows(*args, **kwargs):
    import pyarrow as pa
    return output_arrow(*args, **kwargs, new_writer=pa.ipc.new_stream)


def require_file(urlstr:str):
    from urllib.parse import urlparse

    url = urlparse(urlstr)

    p = Path(url.netloc, *Path(url.path[1:]).parts)

    if not p.exists():
        parentdir = Path(url.netloc, *Path(url.path[1:]).parent.parts)
        parentdir.mkdir(parents=True, exist_ok=True)

        with p.open(mode='wb') as fp:
            import requests
            resp = requests.get(urlstr, stream=True)
            amt = 0
            total = int(resp.headers['Content-length'])
            while b := resp.raw.read(16384):
                fp.write(b)
                amt += len(b)
                print(f'\r{fp.name} {amt*100/total:d}%  {amt}/{total}', end='', file=sys.stderr)

    return p


def unzip(p):
    import zipfile
    return zipfile.ZipFile(p)
