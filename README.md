# Deluxe Datasets

Scripts to convert known datasets into more convenient forms.


## Usage

    scripts/<dataset>.py [options]

Download (and cache) dataset, load into memory, and convert into output format (default parquet).

Options:

- `-f <format>` to output in a specific format, where `<format>` is any number of supported output formats (comma-separated)
- `-o <output_dir>` to output into a specific directory (will be created if not exist)
- `--debug`: stop parsing after 10000 rows

## supported output formats

- `parquet`
- `duckdb`
- `arrow`
- `arrows`
