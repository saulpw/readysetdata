#!sh

set -e

rm -rf output/

for script in $(ls $scripts) ; do
    $script $* -o output
done
