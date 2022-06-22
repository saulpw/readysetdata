import os
import sys

from pathlib import Path


CACHE_DIR='cache'


def download_path(urlstr:str) -> Path:
    from urllib.parse import urlparse

    url = urlparse(urlstr)
    p = Path(CACHE_DIR, url.netloc, *Path(url.path[1:]).parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


class TeeFile:
    def __init__(self, delegate, teepath=None, total=0):
        self._delegate = delegate
        self._teefp = teepath.open(mode='wb') if teepath else None
        self._amtread = 0
        self._total = total

    def read(self, n):
        r = self._delegate.read(n)

        self._amtread += len(r)

        sys.stderr.write(f'\r{self._amtread//2**20}/{self._total//2**20}MB')

        if self._teefp:
            if r:
                self._teefp.write(r)
            else:
                self._teefp.close()

        return r

    def __getattr__(self, k):
        return getattr(self._delegate, k)


def download(urlstr:str):
    p = download_path(urlstr)
    if not p.exists():
        import requests
        resp = requests.get(urlstr, stream=True)
        total = int(resp.headers['Content-length'])
        return TeeFile(resp.raw, p, total=total)

    return TeeFile(p.open(mode='rb'), total=os.stat(p).st_size)
