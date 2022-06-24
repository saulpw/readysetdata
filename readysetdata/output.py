import sys
from pathlib import Path

from readysetdata import get_optarg

from .arrow import *
from .parquet import *
from .duckdb import *
from .sqlite import *
from .jsonl import *


tables = {}


def output(dbname, tblname, rows):
    with OutputTable(dbname, tblname) as out:
        for r in rows:
            out.output(r)


class OutputTable:
    def __init__(self, dbname, tblname, schemastr='', formats=''):
        self.dbname = dbname
        self.tblname = tblname
        self.rowbatch = []
        self.schemastr = schemastr
        self.outputters = []
        self.batch_size = 100

        if not formats:
            formats = get_optarg('-f', 'FORMATS')

        self.formats = [x for x in formats.split(',') if x]

        if not self.formats:
            self.formats = [func[7:]
                    for func in globals()
                        if func.startswith('output_')]

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        for o in self.outputters:
            o.finalize()

    @property
    def dbpath(self):
        outdir = get_optarg('-o', 'OUTDIR', '.')
        Path(outdir).mkdir(parents=True, exist_ok=True)
        return str(Path(outdir)/self.dbname)

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

            if len(self.rowbatch) > self.batch_size:
                batch_dicts = self.rowbatch[:self.batch_size]
                batch_tuples = [tuple(r.values()) for r in batch_dicts]
                for outputter in self.outputters:
                    outputter.output_batch(batch_tuples, batch_dicts)

                del self.rowbatch[:self.batch_size]
