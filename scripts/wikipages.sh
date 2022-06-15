#!/bin/sh

URL="https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2"

scripts/download.py $URL | bunzip2 - \
                         | scripts/xml2jsonl.py page \
                         | jq -c '{title, "text" : .revision["text"]["#text"]}' \
                         | grep '{{Infobox' \
                         | scripts/wp-infobox-extract.py \
                         | scripts/wp-infobox-parse.py
