import json
from pathlib import Path


class JsonlOutputter:
    def __init__(self, fn, schema):
        self.fn = fn
        self.schema = schema

    def output_batch(self, rows_list, rows_dicts):
        with open(fn, 'w') as fp:
            for r in rows_dicts:
                print(json.dumps(r), file=fp)

    def finalize(self):
        pass


def output_jsonl(dbname, tblname, schemastr):
    schema = []
    for field in schemastr.split():
        func = lambda x: x
        if ':' in field:
            fieldname, fieldtype = field.split(':')
        else:
            fieldname = field
        schema.append(fieldname)

    return JsonlOutputter(Path(dbname)/(tblname+'.jsonl'), schema)
