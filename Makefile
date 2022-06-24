OUTPUT=output
ZIP=zip -n .arrow
export LANGS=en,ja

all: movielens geonames wikipedia

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

wikidata:
	OUTDIR=${OUTPUT}/wikidata scripts/wikidata.sh


clean:
	rm -rf ${OUTPUT}
	rm -rf cache/
