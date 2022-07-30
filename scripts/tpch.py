#!/usr/bin/env python3

import sys

import duckdb


def main(outfn='tpch-1gb.duckdb', sf=1.0):
    con = duckdb.connect(outfn)
    con.execute(f'CALL dbgen(sf={sf})')


if __name__ == '__main__':
    main(*sys.argv[1:])
