#!/usr/bin/env python3

import sys

import readysetdata

f = readysetdata.download(sys.argv[1])

blocksize = 65536
while r := f.read(blocksize):
    sys.stdout.buffer.write(r)

sys.stdout.buffer.flush()
f.close()
