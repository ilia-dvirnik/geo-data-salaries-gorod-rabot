# geo-data-salaries-gorod-rabot

Python script for collecting salary data from Gorod Rabot based on a list of cities in Excel.

## Overview

This project collects salary data from Gorod Rabot using a list of cities and source URLs provided in an Excel file.

The script:
- reads an Excel file with city names, region names, and source URLs
- requests salary pages from Gorod Rabot
- parses salary data by year and month
- stores downloaded HTML pages in a local cache
- exports the final result to an Excel file

## Input file

The script expects an Excel file with the following data:
- city name
- region name
- Gorod Rabot URL

Example input columns:
- `Населенный пункт`
- `Регион РФ`
- `Город работ`

The input file itself is not included in the repository.

## Output file

The script saves the result to:

`gorodrabot_salaries.xlsx`

## Cache

The script uses a local cache file:

`gorodrabot_cache.json`

This helps reduce repeated requests to the website and makes reruns faster.

## Requirements

- Python 3
- pandas
- requests
- openpyxl

## Installation

Install dependencies with:

pip install -r requirements.txt

## How to run

### Option 1: Google Colab

Open the script in Google Colab, upload the input Excel file, and run the code.

### Option 2: Local machine

Place the input Excel file in the same folder as the script, then run:

python main.py

## Notes

- The cache file and output files are excluded from GitHub with `.gitignore`.
- The script is designed for data collection and analysis workflows.
- The year range is defined inside the script.
