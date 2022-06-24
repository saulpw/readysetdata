import json


class JsonlOutputter:
    takes_dicts = True
    def __init__(self, fn, schema):
        self.fn = fn
        self.schema = schema
        self.fp = open(fn, 'w')

    def output_batch(self, rows):
        for r in rows:
            print(json.dumps(r), file=self.fp)

    def finalize(self):
        self.fp.close()


def output_jsonl(dbname, tblname, schemastr):
    schema = []
    for field in schemastr.split():
        func = lambda x: x
        if ':' in field:
            fieldname, fieldtype = field.split(':')
        else:
            fieldname = field
        schema.append(fieldname)

    return JsonlOutputter(f'{dbname}-{tblname}.jsonl', schema)

