

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
    takes_dicts = False
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
