#!/usr/bin/env python3

import fileinput
import json

from readysetdata import wikipedia, parse_jsonl

for row in parse_jsonl(fileinput.input()):
    for d in wikipedia.parse_infoboxes(row.revision.text['#text']):
        out = dict(wp_title=row.title)
        out.update(d)
        print(json.dumps(out))
