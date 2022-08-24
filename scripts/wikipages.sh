#!/bin/sh

URL="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"

scripts/download.py $URL \
    | bunzip2 - \
    | scripts/xml2jsonl.py 'page' \
    | FORMATS=jsonl scripts/parse-wikipedia.py
