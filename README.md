# Ready, Set, Data!

A command-line tool and Python library to extract tabular data from any source and save it in any output format.

# Rationale

    I wish to apologize for something that is not my responsibility but is the result of physicists all over the world of scientists (so-called) [who] have been measuring things in different units and cause an enormous amount of complexity.  So as a matter of fact **nearly a third of what you have to learn consists of different ways of measuring the same thing** and I apologize for it.
        -- Feynman Lectures on Physics (17 - Spacetime)

Data formats are the same way and ReadySetData is my apology for it.

# Features

- Reads from local file, stdin, or url (http, s3, imap)
- Detects encoding and format from filename, content, and metadata
- Writes to local file (sqlite, parquet), stdout (json)
- Streaming conversion
- Shows Progress meter on stderr
- Supports containers and compression (zip tar gz)

## Supported formats

- json jsonl
- csv tsv
- html
- sqlite
- xls xlsx
- xlsx
- [Apache Parquet](https://parquet.apache.org/): `parquet`
- [Apache Arrow IPC format](https://arrow.apache.org/docs/cpp/ipc.html): `arrow` and `arrows`
- [DuckDB](https://duckdb.org): `duckdb`
- [SQLite](https://sqlite.org): `sqlite`
- zip
- gz bz2 xz
- zstd

# Installation

Requires Python 3.8+.

    git clone https://github.com/saulpw/readysetdata.git
    cd readysetdata

Then from within the checkout,

    python3 setup.py install

or

    pip3 install -e .

# Usage

    rsd [<input>] [-o <output>] [--option-name=value]

This detects the type of `<input>`, reads the tabular data within, and writes it to `<output>`.
The order of arguments does not matter.

- `input` may be:
  - `-` or missing: stdin
  - URL: http, s3, mysql, imap
  - pathname
    - local file of any type
    - a wildcard of a number of files from an archive/directory

- `output` may be:
  - `-` or missing: stdout (json by default, or csv or tsv)
  - pathname
    - a local file (xlsx, parquet)
    - an archive/directory of local files (zip)
    - a database (sqlite, duckdb)

Available options depend on the input and output format.

Performance varies.

## A universal data converter

     rsd https://example.com/hugefile.zip/*.csv -o hugefile.sqlite

will save each .csv file in hugefile.zip as a table in `hugefile.sqlite`.



----


## Real Data

A collection of interesting datasets and the tools to convert them into ready-to-use formats.

- datasets conform to reasonable standards (UTF-8, RFC3339 dates, decimal lat/long coords, SI units)
- curated and cleaned datasets: quality over quantity
- fields and units are clearly labeled and properly typed

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
