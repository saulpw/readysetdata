#!/usr/bin/env python3

import sys
import re
import json
from pathlib import Path

from dxd.utils import get_optarg


def main(fieldname):
    p = Path(get_optarg('-o'))
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


main(sys.argv[1])
