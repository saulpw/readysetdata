import sys
import re
from pathlib import Path

from readysetdata import get_optarg

from .arrow import *
from .parquet import *
from .duckdb import *
from .sqlite import *
from .jsonl import *


def outputSingle(dbname, tblname, row, **kwargs):
    OutputTable.get(dbname, tblname, **kwargs).output(row)


def output(dbname, tblname, rows):
    with OutputTable(dbname, tblname) as out:
        it = iter(rows)
        while True:
            try:
                r = next(it)
                out.output(r)
            except Exception as e:
                print(str(e), file=sys.stderr)


def cleanid(orig):
    s = orig.lower()
    s = re.sub(r'[^A-Za-z0-9]+', '_', s)
    s = s.strip('_')  # both leading and trailing
    s = s[:100]  # max fn length < 255
    return s


def finish():
    for o in OutputTable._outputs.values():
        o.finalize()

class OutputTable:
    _outputs = {}  # (dbname, clean_tblname) -> OutputTable

    def __init__(self, dbname, tblname, schemastr='', formats='', batch_size=100):
        self.dbname = dbname
        self.tblname = cleanid(tblname)
        self.rowbatch = []
        self.schemastr = schemastr
        self.outputters = []
        self.batch_size = batch_size

        if not formats:
            formats = get_optarg('-f', 'FORMATS')

        self.formats = [x for x in formats.split(',') if x]

        if not self.formats:
            self.formats = [func[7:]
                    for func in globals()
                        if func.startswith('output_')]

    @classmethod
    def get(cls, dbname, tblname, **kwargs):
        tblname = cleanid(tblname)
        k = (dbname, tblname)
        if k not in cls._outputs:
            obj = cls(dbname, tblname, **kwargs)
            cls._outputs[k] = obj

        return cls._outputs[k]

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.finalize()

    def finalize(self):
        for o in self.outputters:
            o.finalize()

    @property
    def dbpath(self):
        outdir = get_optarg('-o', 'OUTDIR', '.')
        p = Path(outdir)/self.dbname
        p.mkdir(parents=True, exist_ok=True)
        return str(p)

    def output(self, *rows):
        for r in rows:
            if not self.outputters:
                if not self.schemastr:
                    self.schemastr = ' '.join(r.keys())

                self.outputters = [
                    globals()[f'output_{fmt}'](self.dbpath, self.tblname, self.schemastr)
                        for fmt in self.formats
                ]

            self.rowbatch.append(r)

            if len(self.rowbatch) >= self.batch_size:
                batch_dicts = self.rowbatch[:self.batch_size]
                batch_tuples = [tuple(r.values()) for r in batch_dicts]
                for outputter in self.outputters:
                    outputter.output_batch(batch_tuples, batch_dicts)

                del self.rowbatch[:self.batch_size]
