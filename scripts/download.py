#!/usr/bin/env python3

import sys

import readydata

f = readydata.download(sys.argv[1])

blocksize = 65536
while r := f.read(blocksize):
    sys.stdout.buffer.write(r)

sys.stdout.buffer.flush()
f.close()
