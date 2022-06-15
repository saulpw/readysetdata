# Deluxe Datasets

Scripts to convert known datasets into more convenient forms.

## What is deluxe data?

Deluxe data is clean, neat, and dense--immediately usable and frequently relevant.

These particular "deluxe datasets" are a curated set of ready-to-use data from the real world.

Deluxe datasets:

  - are downloadable, not behind an API
  - are ~1MB-10GB in size
  - are in an instantly usable format
  - have known downloadable sources (which may be updated regularly)
  - have a known magnitude (not increasing exponentially)
  - conform to common reasonable standards
    - UTF-8
    - RFC 3339/ISO dates
    - lat/long in decimal form
    - SI units
    - units appended to field name like `_km2`
    - `snake_lowercase` field names

### Deluxe datasets are spotless.

Seriously, if you find anything wrong with a deluxe dataset, [please file a bug](issues).
This includes [mojibake](), 0 or other values that should be `null`, or anything else that's amiss.

## Usage

    scripts/<dataset>.py [options]

This will download (and cache) the source data, load it into memory, and convert it into an output format (default parquet).

Options:

- `-f <format>` to output in a specific format, where `<format>` is any number of supported output formats (comma-separated)
- `-o <output_dir>` to output into a specific directory (will be created if not exist)
- `--debug`: stop parsing after 10000 rows

## Supported output formats

- [`parquet`]() (Apache Parquet)
- [`arrow`]() (Apache Arrow IPC)
- [`arrows`]() (Apache Arrow IPC streaming)
- [`duckdb`]() (DuckDB)

# Helper scripts

    scripts/download.py <url>

Download and cache the given URL; write the contents to stdout.

# Credits

Curated and cleaned by Saul Pwanson.

Enabled by [Apache Arrow]() and [Voltron Data]().
