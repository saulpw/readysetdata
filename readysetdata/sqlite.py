from functools import cached_property
import sqlite3

from .utils import AttrDict


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

    def output_batch(self, rowbatch, rowdicts):
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


def attrdict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return AttrDict((k,v) for k,v in zip(fields, row))


class SqliteDatabase:
    def __init__(self, dbfn):
        self.dbfn = dbfn + '.sqlite'
        self.tables = set()

    @cached_property
    def con(self):
        con = sqlite3.connect(self.dbfn)
        con.row_factory = attrdict_factory
        return con

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if not tb:
            self.con.commit()
        return False

    def insert(self, tblname, **kwargs):
        def sqltype(v):
            if isinstance(v, int): return 'INTEGER'
            if isinstance(v, float): return 'REAL'
            return 'TEXT'

        def sqlval(v):
            if v is None: return v
            if isinstance(v, (int, float, str)):
                return v
            return str(v)

        if tblname not in self.tables:
            fieldstr = ', '.join(f'{k} {sqltype(v)}' for k,v in kwargs.items())
            self.con.execute(f'CREATE TABLE IF NOT EXISTS {tblname} ({fieldstr})')
            self.tables.add(tblname)

        fieldnames = ','.join(kwargs.keys())
        valholders = ','.join(['?']*len(kwargs))
        self.con.execute(f'INSERT INTO {tblname} ({fieldnames}) VALUES ({valholders})', tuple(sqlval(x) for x in kwargs.values()))
        return AttrDict(kwargs)

    def table(self, tblname):
        return self.query(f'SELECT * FROM {tblname}')

    def select(self, tblname: str, **kwargs) -> list[AttrDict]:
        sql = f'SELECT * FROM "{tblname}"'
        if kwargs:
            sql += " WHERE "
            sql += " AND ".join([f"{k}=?" for k in kwargs])

        if kwargs:
            return self.query(sql, list(kwargs.values()))
        else:
            return self.query(sql)

    def query(self, qstr, args=[]):
        try:
            cur = self.con.cursor()
            if args:
                res = cur.execute(qstr, args)
            else:
                res = cur.execute(qstr)
            return res.fetchall()
        except sqlite3.OperationalError as e:
            print(e)
            raise
            return []

    def execute(self, qstr):
        return self.con.execute(qstr)

    def commit(self):
        self.con.commit()
