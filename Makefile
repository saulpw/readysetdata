all: movielens geonames wikipedia

setup:
	pip3 install -r requirements.txt

movielens:
	scripts/movielens.py

geonames:
	scripts/geonames-us.py
	scripts/geonames-nonus.py

wikipedia:
	scripts/wikipages.sh
