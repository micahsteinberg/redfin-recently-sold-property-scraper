# Redfin Recently Sold Property Scraper

## Description
Python script to scrapes recently sold properties from redfin.com's database and save them to a csv file
#### Data fields in generated csv:
- property_id
- date_sold
- price
- square_footage
- lot_size
- number_bedrooms
- number_bathrooms
- year_built
- latitude
- longitude
- property_type
- street_number
- street_name
- neighborhood
- city
- state
- zip_code
- time_until_sold

## Instructions
- Start a virtual environment with the dependencies stored in environment.yml. Using conda:
```
conda env create -f environment.yml
source activate redfinscrape
```
- Set global variables in main.py
  - OUT_FILENAME = desired output file name
  - TIME_RANGE = how many days in the past you want sold property information for
- Run using python3:
```
python3 main.py
```
