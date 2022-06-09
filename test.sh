#!sh

set -e

rm -rf test_output/

./scripts/movielens_genome.py --debug -o test_output
./scripts/gnis_us.py --debug -o test_output
