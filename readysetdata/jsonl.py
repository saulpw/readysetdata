import json


class JsonlOutputter:
    def __init__(self, fn, schema):
        self.fn = fn
        self.schema = schema
        self.fp = open(fn, 'w')

    def output_batch(self, rows_list, rows_dicts):
#        for r in rows_dicts:
#            print(json.dumps(r), file=self.fp)
        for r in rows_list:
            print(json.dumps(dict(zip(self.schema, r))), file=self.fp)

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
