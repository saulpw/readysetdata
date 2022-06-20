#!/bin/sh

URL="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"
OUTDIR="output/wp-infoboxes"

rm -rf $OUTDIR
mkdir -p $OUTDIR

tools/download.py $URL \
    | bunzip2 - \
    | tools/xml2jsonl.py 'page' \
    | jq -c '{title, "text" : .revision["text"]["#text"]}' \
    | grep -i '{{infobox' \
    | tee $OUTDIR/raw-infoboxes.jsonl \
    | scripts/wp-infobox-parse.py \
    | tee $OUTDIR/all-infoboxes.jsonl \
    | tools/demux-jsonl.py 'infobox_type' -o $OUTDIR
