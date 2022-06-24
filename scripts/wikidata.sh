#!/bin/sh

URL="https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2"

scripts/download.py $URL \
    | bunzip2 - \
    | scripts/parse-wikidata.py
