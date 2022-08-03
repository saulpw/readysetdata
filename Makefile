OUTPUT=output
ZIP=zip -n .arrow
export LANGS=en,ja

all: movielens geonames wikipedia infoboxes spwdata tpch imdb

setup:
	pip3 install -r requirements.txt

movielens:
	scripts/movielens.py -o ${OUTPUT}
	cd ${OUTPUT} && ${ZIP} movielens.arrowz movielens_*.arrow

geonames:
	scripts/geonames-us.py -o ${OUTPUT}
	scripts/geonames-nonus.py -o ${OUTPUT}
	cd ${OUTPUT} && ${ZIP} geonames.arrowz geonames_*.arrow

infoboxes:
	OUTDIR=${OUTPUT}/wp-infoboxes scripts/wikipages.sh
	cd ${OUTPUT}/wp-infoboxes && ${ZIP} ../wikipedia-infoboxes.zip *.jsonl

wikisummaries:
	/usr/bin/env python3 -m spacy download en_core_web_sm
	OUTDIR=${OUTPUT}/wp-summaries scripts/wikisummaries.sh

wikidata:
	OUTDIR=${OUTPUT}/wikidata scripts/wikidata.sh

fakedata:
	scripts/fakedata.py ${OUTPUT}/fakedata.zip 3

tpch:
	scripts/tpch.py ${OUTPUT}/tpch-1gb.duckdb 1.0

imdb:
	scripts/imdb.py -o ${OUTPUT}

clean:
	rm -rf ${OUTPUT}
	rm -rf cache/
