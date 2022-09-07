#!/usr/bin/env python3

import readysetdata as rsd


def output_imdb(tblname, fn):
    IMDB='https://datasets.imdbws.com/'
    try:
        with rsd.download(IMDB+fn) as fp:
            rsd.output('imdb', tblname, rsd.parse_tsv(rsd.gunzip(fp)))
    except Exception as e:
        print(f"file {fn} failed to output completely: {repr(e)}")


output_imdb('basics', 'title.basics.tsv.gz')
output_imdb('crew', 'title.crew.tsv.gz')
output_imdb('episode', 'title.episode.tsv.gz')
output_imdb('principals', 'title.principals.tsv.gz')
output_imdb('names', 'name.basics.tsv.gz')
output_imdb('ratings', 'title.ratings.tsv.gz')
output_imdb('akas', 'title.akas.tsv.gz')
