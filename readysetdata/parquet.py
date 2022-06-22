from .arrow import parse_schema


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


