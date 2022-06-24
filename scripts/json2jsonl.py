#!/usr/bin/env python3

import fileinput


for i, line in enumerate(fileinput.input()):
    if len(line) > 2:
        print(line.rstrip("\n,"))
