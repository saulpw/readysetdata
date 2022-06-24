from .arrow import parse_schema


class DuckDbOutputter:
    takes_dicts = False
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
