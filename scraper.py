# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import datetime
import sqlite3
from bs4 import BeautifulSoup
from requests import get

# Georges River Council eTrack applications submitted this month
baseurl = "https://etrack.georgesriver.nsw.gov.au/"
scrape_url = (
    baseurl + "Pages/XC.Track/SearchApplication.aspx?d=thismonth&k=LodgementDate&"
)

# sqlite stuff required by morph.io
# Required fields: https://www.planningalerts.org.au/how_to_write_a_scraper
# SQlite documentation: https://morph.io/documentation
table_name = "data"
table_filename = table_name + ".sqlite"

#
# Read in the page and parse it with BS4
soup = BeautifulSoup(get(scrape_url).text, "html.parser")
results = soup.find(id="hiddenresult")

# Write out to the sqlite database using scraperwiki library
sqlite = sqlite3.connect("data.sqlite")
cursor = sqlite.cursor()
with sqlite:
    # Check if table already exists. Create table if not
    cursor.execute(
        f"""
        SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'
        """
    )

    if cursor.fetchone()[0] != 1:
        cursor.execute(
            """
            create table data (
                council_reference varchar unique,
                address text,
                description text,
                info_url text,
                date_scraped date
                )
            """
        )

    # Scrape the application list
    for entry in results("tr"):
        council_reference = entry.find(class_="col2").div.text
        address = ", ".join(
            [
                s.strip()
                for s in entry.find(class_="col3").text.strip().split("\n")
                if s != ""
            ][:-1]
        )
        info_url = baseurl + entry.a.get("href").replace("../../", "")
        description = entry.find(class_="col3").text.split("\n").pop()
        date_scraped = datetime.date.today().strftime("%Y-%m-%d")

        cursor.execute(
            f"""
            insert or replace into data (
                council_reference,
                address,
                description,
                info_url,
                date_scraped)

            values (
                "{council_reference}",
                "{address}",
                "{description}",
                "{info_url}",
                "{date_scraped}"
            )
        """
        )
