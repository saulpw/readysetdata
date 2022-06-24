import os
import sys


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


def get_optarg(arg, envvar=''):
    try:
        i = sys.argv.index(arg)
        return sys.argv[i+1]
    except ValueError:
        if envvar:
            return os.getenv(envvar, '')
        else:
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


class JsonLines:
    def __init__(self, fp):
        self.fp = fp

    def __iter__(self):
        import json

        for line in self.fp:
            if len(line) > 2:
                line = line.rstrip("\n,")
                yield AttrDict(json.loads(line))


def parse_jsonl(fp):
    return JsonLines(fp)
