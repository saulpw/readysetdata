import os
import sys
import time


def stderr(*args, file=sys.stderr):
    sys.stderr.write(str(' '.join(args)))
    sys.stderr.flush()

def warning(*args):
    stderr('\n', *args)


def intfloat(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def getattrdeep(obj, attr, *default, getter=getattr):
    try:
        'Return dotted attr (like "a.b.c") from obj, or default if any of the components are missing.'
        if not isinstance(attr, str):
            return getter(obj, attr, *default)

        try:  # if attribute exists, return toplevel value, even if dotted
            if attr in obj:
                return getter(obj, attr)
        except Exception as e:
            pass

        attrs = attr.split('.')
        for a in attrs[:-1]:
            obj = getter(obj, a)

        return getter(obj, attrs[-1])
    except Exception as e:
        if not default: raise
        return default[0]


def getitem(o, k, default=None):
    return default if o is None else o[k]

def getitemdeep(obj, k, *default):
    return getattrdeep(obj, k, *default, getter=getitem)


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

    def __hasattr__(self, k):
        return k in self

    def __setattr__(self, k, v):
        if k in self:
            self[k] = v
        else:
            super().__setitem__(k, v)

    def update(self, **kwargs):
        keys = list(self.keys())
        super().update({k:v for k,v in kwargs.items() if k in keys})


class Progress:
    def __init__(self, iterator, name=''):
        self.iterator = iterator
        self.name = name
        self.first_time = time.time()
        self.last_time = time.time()

    def __iter__(self):
        for i, x in enumerate(self.iterator):
            t = time.time()

            if t - self.last_time > 0.1:
                stderr(f'\r[{t - self.first_time:.1f}s] {i}')
                self.last_time = t
            yield x


def get_optarg(arg, envvar='', default=''):
    try:
        i = sys.argv.index(arg)
        return sys.argv[i+1]
    except ValueError:
        if envvar:
            return os.getenv(envvar, default)
        else:
            return default


def batchify(rows, n=10000):
    rowbatch = []
    for row in rows:
        rowbatch.append(row)
        if len(rowbatch) >= n:
            yield rowbatch
            rowbatch = []

    if rowbatch:
        yield rowbatch


## extract

def unzip_text(p, fn):
    import zipfile
    import io
    zf = zipfile.ZipFile(p)
    fp = zf.open(fn, 'r')
    return io.TextIOWrapper(fp, 'utf-8')


def unzip(p):
#    from stream_unzip import stream_unzip
    import zipfile
    return zipfile.ZipFile(p)


## parse

def parse_csv(fp):
    import csv
    for r in Progress(csv.DictReader(fp)):
        yield AttrDict(r)


def parse_asv(fp, delim='\t'):
    it = iter(fp)
    hdrs = next(it).split(delim)

    for line in Progress(it):
        yield AttrDict(zip(hdrs, line.split(delim)))


parse_tsv = parse_asv

class JsonLines:
    def __init__(self, fp):
        if isinstance(fp, str):
            fp = open(fp)
        self.fp = fp

    def __iter__(self):
        import json

        for line in Progress(self.fp):
            if len(line) > 2:
                line = line.rstrip("\n,")
                yield AttrDict(json.loads(line))


def parse_jsonl(fp):
    return JsonLines(fp)

def gunzip(fp, encoding='utf-8'):
    import gzip
    mode = 'rt' if encoding else 'rb'
    return gzip.open(fp, mode=mode, encoding=encoding)
