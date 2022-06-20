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

class Progress:
    def __init__(self, iterator, name=''):
        self.iterator = iterator
        self.name = name

    def __iter__(self):
        for i, x in enumerate(self.iterator):
            yield x
            if i % 10000 == 0:
                print(f'\r{self.name} {i}', end='', file=sys.stderr)
                sys.stderr.flush()
                if debug and i:
                    break

        print('', file=sys.stderr)


def csv(fp):
    import csv
    for r in Progress(csv.DictReader(fp), fp.name):
        yield AttrDict(r)


def asv(fp, delim='\t'):
    it = iter(fp)
    hdrs = next(it).split(delim)

    for line in Progress(it, fp.name):
        yield AttrDict(zip(hdrs, line.split(delim)))



class JsonLines:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        import json

        for line in Progress(self.fp, self.fp.name):
            yield AttrDict(json.loads(line))


def jsonl(fp):
    return JsonLines(fp)


def get_optarg(arg):
    try:
        i = sys.argv.index(arg)
        return sys.argv[i+1]
    except ValueError:
        return ''


def batchify(rows, n=10000):
    rowbatch = []
    for row in rows:
        rowbatch.append(row)
        if len(rowbatch) >= n:
            yield rowbatch
            rowbatch = []

    if rowbatch:
        yield rowbatch


def output(dbname, tblname, schemastr, rows):
    fmtstr = get_optarg('-f')

    if fmtstr:
        fmts = fmtstr.split(',')
    else:
        fmts = [func.removeprefix('output_')
                  for func in globals()
                    if func.startswith('output_')]

    outdir = get_optarg('-o') or '.'
    Path(outdir).mkdir(parents=True, exist_ok=True)

    dbpath = str(Path(outdir)/dbname)

    for i, rowbatch in enumerate(batchify(rows)):
        if i == 0:  # first batch
            outputters = [
                globals()[f'output_{fmt}'](dbpath, tblname, schemastr)
                    for fmt in fmts
            ]
        for outputter in outputters:
            outputter.output_batch(rowbatch)

    for outputter in outputters:
        outputter.finalize()


class ParquetOutputTable:
    def __init__(self, fn, schema):
        self.fn = fn
        self.rows = []
        self.schema = schema

    def output_batch(self, rowbatch):
        self.rows.extend(rowbatch)

    def finalize(self):
        import pyarrow.parquet as pq
        import pyarrow as pa

        pq.write_table(pa.table(list(zip(*self.rows)), schema=pa.schema(self.schema)), self.fn)


def output_parquet(dbname, tblname, schemastr):
    return ParquetOutputTable(f'{dbname}_{tblname}.parquet', parse_schema(schemastr))


class DuckDbOutputter:
    def __init__(self, fn, tblname, schema):
        import duckdb

        self.fn = fn
        self.tblname = tblname
        self.schema = schema
        self.con = duckdb.connect(fn)
        self.table_created = False

    def output_batch(self, rowbatch):
        import pyarrow as pa

        tbl = pa.table(list(zip(*rowbatch)), schema=pa.schema(self.schema))
#        tbl = pa.table([
#            pa.array([r[i] for r in rowbatch], type=fieldtype)
#                for i, (fieldname, fieldtype) in enumerate(self.schema)
#        ])

        if not self.table_created:
            self.con.execute(f"DROP TABLE IF EXISTS {self.tblname}")
            self.con.execute(f"CREATE TABLE {self.tblname} AS SELECT * FROM tbl")
            self.table_created = True
        else:
            self.con.execute(f"INSERT INTO {self.tblname} SELECT * FROM tbl")

    def finalize(self):
        self.con.close()


def output_duckdb(dbname, tblname, schemastr):
    return DuckDbOutputter(f'{dbname}.duckdb', tblname, parse_schema(schemastr))


def arrow_gettype(s):
    import pyarrow as pa

    if s[0] == 'A':
        return pa.list_(arrow_gettype(s[1:]))

    if not s:
        return pa.string()

    return {
        'f': pa.float32(),
        'd': pa.float64(),
        'i': pa.int32(),
        'l': pa.int64(),
        'b': pa.int8(),
    }.get(s, pa.string())


def parse_schema(schema):
    import pyarrow as pa

    ret = []
    for fieldname in schema.split():
        if ':' in fieldname:
            fieldname, fieldtype = fieldname.split(':')
            fieldtype = arrow_gettype(fieldtype)
        else:
            fieldtype = pa.string()

        ret.append((fieldname, fieldtype))

    return ret


def output_arrow(dbname, tblname, schemastr):
    return ArrowOutput(f'{dbname}_{tblname}.arrow', parse_schema(schemastr))


def output_arrows(dbname, tblname, schemastr):
    return ArrowOutput(f'{dbname}_{tblname}.arrows', parse_schema(schemastr), stream=True)


class ArrowOutput:
    def __init__(self, fn, schema, stream=False):
        import pyarrow as pa

        self.fp = open(fn, mode='wb')
        self.schema = schema
        if stream:
            self.writer = pa.ipc.new_stream(self.fp, pa.schema(schema))
        else:
            self.writer = pa.ipc.new_file(self.fp, pa.schema(schema))

    def output_batch(self, rowbatch):
        import pyarrow as pa
        data = [
            pa.array([r[i] for r in rowbatch], type=fieldtype)
                for i, (fieldname, fieldtype) in enumerate(self.schema)
        ]
        self.writer.write_batch(pa.record_batch(data, schema=pa.schema(self.schema)))

    def finalize(self):
        self.writer.close()
        self.fp.close()


def download(urlstr:str):
    from urllib.parse import urlparse

    url = urlparse(urlstr)

    p = Path('downloads', url.netloc, *Path(url.path[1:]).parts)

    if not p.exists():
#        parentdir = Path('downloads', url.netloc, *Path(url.path[1:]).parent.parts)
        p.parent.mkdir(parents=True, exist_ok=True)

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


def unzip_text(p, fn):
    import zipfile
    import io
    zf = zipfile.ZipFile(p)
    fp = zf.open(fn, 'r')
    return io.TextIOWrapper(fp, 'utf-8')


def unzip(p):
    import zipfile
    return zipfile.ZipFile(p)
