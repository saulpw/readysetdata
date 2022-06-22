from dataclasses import dataclass

import urllib3
import io
import zlib
import struct


@dataclass
class RemoteZipInfo:
    filename:str = ''
    date_time:int = 0
    header_offset:int = 0
    compress_type:int = 0
    compress_size:int = 0
    file_size:int = 0


class RemoteZipFile:
    fmt_endcdir = 'IHHHHIIH'
    fmt_cdirentry = '<IHHHHIIIIHHHHHII'
    fmt_localhdr = '<IHHHIIIIHH'

    def __init__(self, url):
        self.url = url

    @property
    def http(self):
        return urllib3.PoolManager()

    @property
    def files(self):
        return {r.filename:r for r in self.infolist()}

    def infolist(self):
        resp = self.http.request('HEAD', self.url)
        r = resp.headers.get('Accept-Ranges', '')
        if r != 'bytes':
            raise Exception(f"Accept-Ranges header must be 'bytes' ('{r}')")

        sz = int(resp.headers['Content-Length'])
        resp = self.get_range(sz-65536, 65536)
        i = resp.data.rfind(b'\x50\x4b\x05\x06')

        magic, disk_num, disk_start, disk_num_records, total_num_records, cdir_bytes, cdir_start, comment_len = struct.unpack_from(self.fmt_endcdir, resp.data, offset=i)

        filehdr_index = 65536 - (sz - cdir_start)
        cdir_end = filehdr_index + cdir_bytes
        while filehdr_index < cdir_end:
            sizeof_cdirentry = struct.calcsize(self.fmt_cdirentry)

            magic, ver, ver_needed, flags, method, date_time, crc, \
                complen, uncomplen, fnlen, extralen, commentlen, \
                disknum_start, internal_attr, external_attr, local_header_ofs = \
                    struct.unpack_from(self.fmt_cdirentry, resp.data, offset=filehdr_index)

            filename = resp.data[filehdr_index+sizeof_cdirentry:filehdr_index+sizeof_cdirentry+fnlen]

            filehdr_index += sizeof_cdirentry + fnlen + extralen + commentlen

            yield RemoteZipInfo(filename.decode(), date_time, local_header_ofs, method, complen, uncomplen)

    def get_range(self, start, n):
        return self.http.request('GET', self.url, headers={'Range': f'bytes={start}-{start+n}'}, preload_content=False)

    def open(self, f):
        if isinstance(f, str):
            f = self.files[fn]

        sizeof_localhdr = struct.calcsize(self.fmt_localhdr)
        r = self.get_range(f.header_offset, sizeof_localhdr)
        magic, ver, flags, method, dos_datetime, crc, complen, uncomplen, fnlen, extralen = struct.unpack_from(self.fmt_localhdr, r.data)
        if method == 0: # none
            return self.get_range(f.header_offset + sizeof_localhdr + fnlen + extralen, complen)
        elif method == 8: # DEFLATE
            resp = self.get_range(f.header_offset + sizeof_localhdr + fnlen + extralen, complen)
            return RemoteZipStream(resp)
        else:
            raise Exception(f'unknown compression method {method}')


class RemoteZipStream(io.RawIOBase):
    def __init__(self, fp):
        self.raw = fp
        self._decompressor = zlib.decompressobj(-15)
        self._buffer = bytes()

    def readable(self):
        return True

    def readall(self):
        raise

    def readinto(self, b, /):
        r = self.read(len(b))
        b[:] = r
        return len(r)

    def write(self, b, /):
        raise

    def read(self, n):
        while n > len(self._buffer):
            r = self.raw.read(65536)
            if not r:
                break
            self._buffer += self._decompressor.decompress(r)

        ret = self._buffer[:n]
        self._buffer = self._buffer[n:]
        return ret
