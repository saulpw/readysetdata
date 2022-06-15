#!/usr/bin/env python

import sys
import shutil

from dxd.utils import download

with open(download(sys.argv[1]), mode='rb') as f:
    shutil.copyfileobj(f, sys.stdout.buffer)
