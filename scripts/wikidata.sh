#!/bin/sh

#URL="https://wikimedia.bringyour.com/wikidatawiki/20220601/wikidatawiki-20220601-pages-articles.xml.bz2"
URL="https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2"
OUTDIR="output/wikidata"

rm -rf $OUTDIR
mkdir -p $OUTDIR

scripts/download.py $URL \
    | bunzip2 - \
    | scripts/json2jsonl.py \
    | scripts/parse-wikidata.py
