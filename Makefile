ARGS=-o output

all: movielens geonames wikipedia

setup:
	pip3 install -r requirements.txt

movielens:
	PYTHONPATH=. scripts/movielens.py ${ARGS}

geonames:
	PYTHONPATH=. scripts/geonames-us.py ${ARGS}
	PYTHONPATH=. scripts/geonames-nonus.py ${ARGS}

infoboxes:
	PYTHONPATH=. scripts/wikipages.sh

clean:
	rm -rf cache/
	rm -rf output/
