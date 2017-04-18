#!/bin/bash

filename="clcarstrucks"

rm "$filename.csv"

# search_args = {
#     'auto_make_model': 'honda fit',
#     'auto_title_status': '1', #{"1": "clean", "2": "salvage", "3": "rebuilt", "4": "parts only", "5": "lien", "6": "missing"}
#     'auto_transmission': '2', #{"1": "manual", "2": "automatic", "3": "other"}
#     'min_price': '300',
#     'max_price': '100000',
#     'min_auto_miles': '1000',
#     'max_auto_miles': '100000',
#     'min_auto_year': '2011',
#     'max_auto_year': '2017',
#     'postal': '98133',
#     'search_distance': '30'
# }
# search_args=-a city=seattle -a auto_make_model="honda fit" -a auto_title_status=1 -a auto_transmission=2 -a max_auto_miles=100000 -a min_auto_year=2011 -a postal=98133 -a search_distance=30

source env/bin/activate

scrapy runspider clcarstrucks.py -a city=seattle -a auto_make_model="honda fit" -a auto_title_status=1 -a auto_transmission=2 -a max_auto_miles=100000 -a min_auto_year=2011 -a postal=98133 -a search_distance=30 -o "$filename.csv"

python gdriveimportcsv.py $filename
