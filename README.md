# clcarstrucks
Craigslist cars and trucks search data scraper and google sheets importer

## Getting started
You should set this up in a [virtualenv](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/), which you should be able to install in a few commands (instructions vary by OS).
1. then do `virtualenv env` and then `source env\bin\activate` to create and activate a python virtualenv
2. `pip install -r requirements.txt` to install the project's python dependencies

At this point you should have everything you need to scrape craigslist working to a point where you can generate .csv files on your local machine.  

Try running this as a test:

`scrapy runspider clcarstrucks.py -o test.csv -a city=seattle -a auto_make_model="honda fit" -a auto_title_status=1 -a auto_transmission=2 -a max_auto_miles=10000 -a min_auto_year=2011 -a postal=98133 -a search_distance=10`

If you see a few results in test.csv, you should be good to start hacking around with the search arguments, or editing clcarstrucks.py to your particular needs.

If you wish to import the .csv results into a google sheets document, a bit more setup is required.
1. Go to the [google cloud console dashboard](https://console.cloud.google.com/home/dashboard) and create a new project
2. [Create Oauth client ID credential](https://console.cloud.google.com/apis/credentials) and follow any prompts.  Besides "product name" on the oauth consent screen, you can leave it as defaults to get up and running, and save to get to the actual credential creation.
3. For the "Application type" select "other" name it anything you want, and save.
4. Download the JSON secrets file for this credential to the project directory, and rename it `client_secret.json`. ![screenshot](https://www.dropbox.com/s/yzpe4qzpx4l3x1e/Screenshot%202017-04-19%2000.36.32.png?dl=1 "Download client_secret.json")
5. Go back to the [google cloud console dashboard](https://console.cloud.google.com/home/dashboard) and enable both the Google Drive API and the Google Sheets API for this project.

Now, you should be able to go end to end with this!
Try `./run.sh` and see if you get an oath2 consent screen after a bit in your browser (on localhost:8080).  If so, there should be a clcarstrucks document in google sheets!

If you wish to do any analysis on the data in sheets, I recommend creating another sheets document that references the clcarstrucks document using the =IMPORTRANGE() function so that future scrapes don't destroy your work. `=IMPORTRANGE("https://docs.google.com/spreadsheets/d/SOME_DOCUMENT_ID_HERE", "clcarstrucks!A1:Z5000")`
