# geo-data-salaries-gorod-rabot
Python script for collecting salary data from Gorod Rabot based on a list of cities in Excel

## What the script does

- reads an Excel file with cities and source URLs
- requests salary pages from Gorod Rabot
- parses data by year and month
- stores downloaded HTML in a local cache
- exports the final result to an Excel file

## Input file

The script expects an Excel file with city names, region names, and Gorod Rabot URLs.

## Output file

The result is saved as:

`gorodrabot_salaries.xlsx`

## Notes

The script uses caching to reduce the number of repeated requests to the website.

## Requirements

- Python 3
- pandas
- requests
- openpyxl

## Install

```bash
pip install -r requirements.txt
