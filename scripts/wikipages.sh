#!/bin/sh

URL="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"
OUTDIR="output/wpinfoboxes"

rm -rf $OUTDIR
mkdir -p $OUTDIR

scripts/download.py $URL \
    | bunzip2 - \
    | scripts/xml2jsonl.py 'page' \
    | grep -i '{{infobox' \
    | scripts/parse-wpinfobox.py \
    | scripts/demux-jsonl.py 'infobox_type' $OUTDIR


cd $OUTDIR && zip ../wikipedia-infoboxes.zip *
