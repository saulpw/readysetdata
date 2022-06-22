#!/usr/bin/env python3

'''
Usage:
    remote-unzip <url>.zip <filenames..>

Extracts a file from a remote .zip file and writes to stdout.  HTTP server must send `Accept-Ranges: bytes` and `Content-Length` in headers.

<filename> can be a wildcard glob; all matching files are concatenated and sent to stdout in the order of the zipfile.
'''

import readysetdata as rsd

import io
import sys
import fnmatch


def main(url, *globs):
    rzf = rsd.RemoteZipFile(url)
    for f in rzf.infolist():
        if not globs:
            print(f'{f.compress_size/2**20:.02f}MB -> {f.file_size/2**20:.02f}MB  {f.filename}')
        elif any(fnmatch.fnmatch(f.filename, g) for g in globs):
            fp = rzf.open(f)
            while r := fp.read(65536):
                sys.stdout.buffer.write(r)


main(*sys.argv[1:])
