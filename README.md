# Ready, Set, Data!

A collection of interesting datasets and the tools to convert them into ready-to-use formats.

# Features

- curated and cleaned datasets: quality over quantity
- all tools and pipelines are streaming: first results are available immediately
- fields and units are clearly labeled and properly-typed
- data is output in immediately usable formats (Parquet, Arrow, DuckDB, SQLite)
- datasets conform to reasonable standards (UTF-8, RFC3339 dates, decimal lat/long coords, SI units)

# Setup

Requires Python 3.8+.

    git clone https://github.com/saulpw/readysetdata.git
    cd readysetdata

Then from within the repository,

    make setup

or

    pip install .

or

    python3 setup.py install

# Datasets

Output is generated for all available formats and put in the `OUTPUT` directory (`output/` by default).
Size and time estimates are for JSONL output on a small instance.

## `make movielens` (150MB, 3 tables, 5 minutes) (2019)

- 84k movies and 28m ratings from [MovieLens](https://movielens.org/)

## `make imdb` (20GB, 7 tables, 1 hour; updated daily)

- 9m movies/tv (1m rated), 7m tv episodes, 12m people from [imdb](https://www.imdb.com/interfaces/).

## `make geonames` (500MB, 2 tables, 10 minutes; updated quarterly)

- 2.2m US place names and lat/long coordinates from [USGS GNIS](https://www.usgs.gov/tools/geographic-names-information-system-gnis)
- 13.6m non-US places from [NGA GNS](https://geonames.nga.mil/gns/html/).

## `make wikipedia` (2.5GB, 3800+ categories, 12 hours; updated monthly)

- 4m Wikipedia infoboxes organized by type, in JSONL format
- Xm article summaries (first paragraph and first sentence)

See results immediately as they accumulate in `output/wp-infoboxes`.

## `make tpch` (500MB, 8 tables, 20 seconds; generated randomly)

- [TPC-H](https://www.tpc.org/tpc_documents_current_versions/pdf/tpc-h_v3.0.1.pdf) data generated with [DuckDB](https://duckdb.org/))

## `make fakedata` (13MB, 3 tables, 5 seconds; generated randomly)

- generated with [Faker](https://faker.readthedocs.io/en/master/)
- joinable products, customers, and orders tables for a fake business
- unicode data, including japanese and arabic names and addresses
- includes geo lat/long coords, numeric arrays, and arrays of structs

# Supported output formats

Specify with `-f <formats>` to individual scripts.  Separate multiple formats by `,`.  All available formats will be output by default.

- [Apache Parquet](https://parquet.apache.org/): `parquet`
- [Apache Arrow IPC format](https://arrow.apache.org/docs/cpp/ipc.html): `arrow` and `arrows`
- [DuckDB](https://duckdb.org): `duckdb`
- [SQLite](https://sqlite.org): `sqlite`

# Scripts

These live in the `scripts/` directory.  Some of them require the `readysetdata` module to be installed.  For the moment, set `PYTHONPATH=.` and run from the toplevel directory.

## `remote-unzip.py <url> <filename>`

Extract `<filename>` from .zip file at `<url>`, and stream to stdout.  Only downloads the one file; does not need to download the entire .zip.

## `download.py <url>`

Download from `<url>` and stream to stdout.  The data for e.g. `https://example.com/path/to/file.csv` will be cached at `cache/example.com/path/to/file.csv`.

## `xml2json.py <tag>`

Parse XML from stdin, and emit JSONL to stdout for the given `<tag>`.

## `demux-jsonl.py <field>`

Parse JSONL from stdin, and append each JSONL verbatim to its `<field-value>.jsonl`.

# Credits

Created and curated by [Saul Pwanson](https://saul.pw).  Licensed for use under Apache 2.0.

Enabled by [Apache Arrow](https://arrow.apache.org/) and [Voltron Data](https://voltrondata.com).

Toponymic information is based on the Geographic Names Database, containing official standard names approved by the United States Board on Geographic Names and maintained by the National Geospatial-Intelligence Agency.More information is available at the Resources link at www.nga.mil. TheNational Geospatial-Intelligence Agencyname, initials, and seal are protected by 10 United States Code � Section 425.
