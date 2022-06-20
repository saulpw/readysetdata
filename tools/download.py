#!/usr/bin/env python

import os
import sys
import shutil

from dxd.utils import download

f = download(sys.argv[1])

blocksize = 65536
while r := f.read(blocksize):
    sys.stdout.buffer.write(r)

sys.stdout.buffer.flush()
f.close()
