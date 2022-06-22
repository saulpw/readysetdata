ARGS=-o output

all: movielens geonames wikipedia

setup:
	pip3 install -r requirements.txt

movielens:
	scripts/movielens.py ${ARGS}

geonames:
	scripts/geonames-us.py ${ARGS}
	scripts/geonames-nonus.py ${ARGS}

wikipedia:
	scripts/wikipages.sh
