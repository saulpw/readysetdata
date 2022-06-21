#!/usr/bin/env python3

'''
Usage: $0 <fieldname> <output_dir>

Demux JSONL from stdin into separate files in <output_dir> based on the <fieldname> in each JSON object.
'''


import sys
import re
import json
from pathlib import Path


def main(fieldname, output_dir):
    p = Path(output_dir)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

    for line in sys.stdin:
        row = json.loads(line)
        s = row[fieldname].lower()
        s = re.sub(r'[^A-Za-z0-9]+', '_', s)
        s = s.strip('_')  # both leading and trailing
        s = s[:100]  # max fn length < 255
        with open(p/(s+".jsonl"), 'a') as fp:
            fp.write(line)


main(*sys.argv[1:])
