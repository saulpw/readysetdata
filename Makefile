OUTPUT=output
ARGS=-o ${OUTPUT}

all: movielens geonames wikipedia

setup:
	pip3 install -r requirements.txt

movielens:
	PYTHONPATH=. scripts/movielens.py ${ARGS}
	cd ${OUTPUT} && zip movielens.arrowz movielens_*.arrow

geonames:
	PYTHONPATH=. scripts/geonames-us.py ${ARGS}
	PYTHONPATH=. scripts/geonames-nonus.py ${ARGS}
	cd ${OUTPUT} && zip geonames.arrowz geonames_*.arrow

infoboxes:
	PYTHONPATH=. scripts/wikipages.sh
	cd ${OUTPUT}/wp-infoboxes && zip ../wikipedia-infoboxes.zip *.jsonl

clean:
	rm -rf ${OUTPUT}
	rm -rf cache/
