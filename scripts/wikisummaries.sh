#!/bin/sh

URL="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"

scripts/download.py $URL \
    | bunzip2 - \
    | scripts/xml2jsonl.py 'page' \
    | grep -v "#REDIRECT" \
    | scripts/parse-wpsummaries.py \
    | scripts/demux-jsonl.py 'shard' $OUTDIR
