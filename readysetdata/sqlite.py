import sqlite3


def struct_to_sqlite_type(s):
    if s in 'bBhHiIlLqQnN': return 'INTEGER'
    if s in 'efd': return 'REAL'
    return 'TEXT'


class SqliteOutputter:
    def __init__(self, fn, tblname, schema):
        self.fn = fn
        self.tblname = tblname
        self.schema = schema
        self.con = sqlite3.connect(fn)
        self.table_created = False

    def output_batch(self, rowbatch):
        if not self.table_created:
            self.con.execute(f"DROP TABLE IF EXISTS {self.tblname}")
            self.con.execute(f"CREATE TABLE {self.tblname} (%s)" % ', '.join(f'{k} {v}' for k, v, _ in self.schema))
            self.table_created = True
        else:
            self.con.executemany(f"INSERT INTO {self.tblname} (%s) VALUES (%s)" % (
                ','.join(name for name, _, _ in self.schema),
                ','.join(['?']*len(self.schema))),
                [[f(x) if x else None for x, (_, _, f) in zip(row, self.schema)] for row in rowbatch])

        self.con.commit()

    def finalize(self):
        self.con.close()


def output_sqlite(dbname, tblname, schemastr):
    schema = []
    for field in schemastr.split():
        func = lambda x: x
        if ':' in field:
            fieldname, fieldtype = field.split(':')
            if fieldtype[0] == 'A':
                func = '|'.join
            schema.append((fieldname, struct_to_sqlite_type(fieldtype), func))
        else:
            schema.append((field, "TEXT", func))

    return SqliteOutputter(f'{dbname}.sqlite', tblname, schema)
