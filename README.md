# Ready, Set, Data!

A collection of interesting datasets and the tools to convert them into ready-to-use formats.

# Features

- curated and cleaned datasets: quality over quantity
- all tools and pipelines are streaming: no waiting for first results
- fields and units are clearly labeled and properly-typed
- data is output in immediately usable formats (Parquet, Arrow, DuckDB)
- datasets conform to reasonable standards (UTF-8, RFC3339 dates, decimal lat/long coords, SI units)

# Install

Requires Python 3.8+.

    make setup

or

    pip install -r requirements.txt

# Datasets

Output is generated for all available formats and put in the `OUTPUT` directory (`output/` by default).

## `make infoboxes` (2.5GB)

- 4m Wikipedia infoboxes organized by type, in JSONL format.

    scripts/wikipages.sh

See results immediately as they accumulate in `output/wp-infoboxes`!

## `make geonames` (500MB)

- 2.2m US place names and lat/long coordinates from [USGS GNIS](https://www.usgs.gov/tools/geographic-names-information-system-gnis)
- 13.6m non-US places from [NGA GNS](https://geonames.nga.mil/gns/html/).

## `make movielens` (125MB)

- 84k movies and 28m ratings from [MovieLens](https://movielens.org/)

# Supported output formats

Specify with `-f <formats>` to individual scripts.  Separate multiple formats by `,`.  All available formats will be output by default.

- [Apache Parquet](https://parquet.apache.org/): `parquet`
- [Apache Arrow IPC format](https://arrow.apache.org/docs/cpp/ipc.html): `arrow` and `arrows`
- [DuckDB](https://duckdb.org): `duckdb`

# Tools

## `scripts/remote-unzip.py <url> <filename>`

Extract `<filename>` from .zip file at `<url>`, and stream to stdout.  Only downloads the one file; does not need to download the entire .zip.

## `scripts/download.py <url>`

Download from `<url>` and stream to stdout.  The data for e.g. `https://example.com/path/to/file.csv` will be cached at `cache/example.com/path/to/file.csv'.

## `scripts/xml2json.py <tag>`

Parse XML from stdin, and emit JSONL to stdout for the given `<tag>`.

## `scripts/demux-jsonl.py <field>`

Parse JSONL from stdin, and append each JSONL verbatim to its `<field-value>.jsonl`.

# Credits

Created and curated by [Saul Pwanson](https://saul.pw).

Enabled by [Apache Arrow](https://arrow.apache.org/) and [Voltron Data](https://voltrondata.com).
