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

## Use case

This tool is designed for geoanalytics and market analysis workflows.

It can be used to:
- estimate salary levels across different cities
- support location-based decision making
- enrich datasets for analytical models

## Input file

The script expects an Excel file with the following data:
- city name
- region name
- Gorod Rabot URL

Example input columns:
- `Города`
- `Субъект РФ`
- `Город работ`

The input file itself is not included in the repository.

## Data coverage

By default, the script collects data for:

- 2025
- current year (automatically)

The year range can be adjusted in the code:

START_YEAR = 2025  
END_YEAR = datetime.now().year  

You can modify these values to collect data for other periods.

## Data sources

The script uses publicly available data from Gorod Rabot.

The input dataset (list of cities and URLs) is not included in the repository.

## Limitations

- The script depends on the current structure of the Gorod Rabot website.
- If the website layout changes, parsing logic may require updates.
- Large-scale data collection should be performed with reasonable request intervals.

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
