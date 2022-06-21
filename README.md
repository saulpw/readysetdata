# Ready Data

A curated collection of interesting datasets and the scripts needed to convert them into a ready-to-use format.

## What makes data ready-to-use

- in an instantly usable format (Parquet, Arrow, DuckDB, Sqlite)
- no parsing required
- structurally convenient
- clearly labeled tables, fields, and units
- properly-typed (both data types and units)
- conforming to reasonable standards (UTF-8, RFC3339 dates, decimal lat/long coords, SI units)
- can be downloaded and used locally (under 10GB)

## Datasets available

* Movie metadata and ratings (84k movies and 28m ratings; 125MB)
* Geographical place names and coordinates (2.2m US and 13.6m non-US; 500MB)
* Wikipedia infoboxes (4m infoboxes; 2.5GB)

# Install

## Requirements

- Python 3.8+
- Python modules listed in requirements.txt
- [jq](https://stedolan.github.io/jq/)

    pip install -r requirements.txt

# Usage

## Wikipedia Infoboxes

All infoboxes organized by type, in JSONL format.  See results in `output/wp-infoboxes` as the source xml.bz2 streams in!

    scripts/wikipages.sh

## Geonames

Lists of place names and lat/long coordinates.

- 2m+ US places from [USGS GNIS](https://www.usgs.gov/tools/geographic-names-information-system-gnis)
- 13m+ non-US places [NGA GNS](https://geonames.nga.mil/gns/html/).

    scripts/geonames-us.py [options]
    scripts/geonames-nonus.py [options]

## [MovieLens](https://movielens.org/)

Movie metadata, ratings, and genres.

    scripts/movielens.py [options]

### Options

- `-f <format>` to output in a specific format, where `<format>` is any number of supported output formats (comma-separated)
- `-o <output_dir>` to output into a specific directory (will be created if not exist)
- `--debug`: stop parsing after 10000 rows

## Supported output formats

Specify with `-o`; multiple formats separated with `,`.  If not specified, all available formats will be output.

- [Apache Parquet](https://parquet.apache.org/): `parquet`
- [Apache Arrow IPC format](https://arrow.apache.org/docs/cpp/ipc.html): `arrow` and `arrows`
- [DuckDB](https://duckdb.org): `duckdb`

# Helper tools

## `tools/download.py <url>`

Download from `<url>` and stream to stdout.  The data for e.g. `https://example.com/path/to/file.csv` will be cached at `cache/example.com/path/to/file.csv'.

## `tools/xml2json.py <tag>`

Parse XML from stdin, and emit JSONL to stdout for the given `<tag>`.

## `tools/demux-jsonl.py <field>`

Parse JSONL from stdin, and append each JSONL verbatim to its `<field-value>.jsonl`.

# Credits

Curated and cleaned by [Saul Pwanson](https://saul.pw).

Enabled by [Apache Arrow](https://arrow.apache.org/) and [Voltron Data](https://voltrondata.com).
