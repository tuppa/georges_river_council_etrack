# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import datetime
from bs4 import BeautifulSoup
from requests import get
import sqlite3

# Georges River Council eTrack applications submitted this month
url = "https://etrack.georgesriver.nsw.gov.au/Pages/XC.Track/SearchApplication.aspx?d=thismonth&k=LodgementDate&"

#
# Read in the page and parse it with BS4
soup = BeautifulSoup(get(url).text, 'html.parser')
results = soup.find(id="hiddenresult")

# Write out to the sqlite database using scraperwiki library
# Required fields: https://www.planningalerts.org.au/how_to_write_a_scraper
# SQlite documentation: https://morph.io/documentation
sqlite = sqlite3.connect('data.sqlite')
with sqlite:
    sqlite.execute('''
        create table data (
            council_reference varchar unique,
            address text,
            info_url text,
            description text
            )
    ''')

    # Scrape the application list
    for entry in results('tr'):
        council_reference = entry.find(class_="col2").div.text
        address = entry.find(class_="col3").text.strip()
        info_url = entry.a.get('href')
        description = entry.find(class_="col3").text.split('\n').pop()
        date_scraped = datetime.date.today().strftime("%Y-%m-%d")


        sqlite.execute(f'''
            insert into data (
                council_reference,
                address,
                info_url,
                description)

            values (
                "{council_reference}",
                "{description}",
                "{info_url}",
                "{date_scraped}"
            )
        ''')
