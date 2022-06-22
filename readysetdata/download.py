import os
import sys

from pathlib import Path
import urllib3


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

        sys.stderr.write(f'\r{self._amtread/10**6:.02f}/{self._total/10**6:.02f}MB {Path(self._delegate.name).name}')

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
        resp = urllib3.PoolManager().request('GET', urlstr, preload_content=False)
        total = int(resp.headers['Content-length'])
        resp.name = Path(urlstr).name
        return TeeFile(resp, p, total=total)

    return TeeFile(p.open(mode='rb'), total=os.stat(p).st_size)
