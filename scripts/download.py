#!/usr/bin/env python

import os
import sys
import shutil

from dxd.utils import download

p = download(sys.argv[1])

total = os.stat(p).st_size
blocksize = 4096
written = 0
with open(p, mode='rb') as f:
    while r := f.read(blocksize):
        sys.stdout.buffer.write(r)
        written += len(r)
        sys.stderr.write(f'\r{written//2**20}/{total//2**20}MB')
