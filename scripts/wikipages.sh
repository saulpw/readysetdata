#!/bin/sh

URL="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"
OUTDIR="output/wikipedia-infoboxes"

rm -rf $OUTDIR
mkdir -p $OUTDIR

scripts/download.py $URL \
    | bunzip2 - \
    | scripts/xml2jsonl.py 'page' \
    | jq -c '{title, "text" : .revision["text"]["#text"]}' \
    | grep -i '{{infobox' \
    | tee $OUTDIR/raw-infoboxes.jsonl \
    | scripts/wp-infobox-parse.py \
    | tee $OUTDIR/all-infoboxes.jsonl \
    | scripts/demux-jsonl.py 'category' -o $OUTDIR
