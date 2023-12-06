import glob
import csv
from os import path
import sys

import urllib3
from collections import namedtuple
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs,urlunparse
import html5lib
from datetime import datetime


# New function for pre-processing row_data
def preprocess_row_data(row_data):
    # Step 1: Drop the 6th column (index=5)
    row_data = row_data[:5] + row_data[6:]

    # Step 2: Parse the second and fifth columns as dates and format them
    date_format = "%d %b %Y"
    go_date = datetime.strptime(row_data[1], date_format)
    gazette_week_date = datetime.strptime(row_data[4], date_format)
    row_data[1] = go_date.strftime("%Y-%m-%d")
    row_data[4] = gazette_week_date.strftime("%Y-%m-%d")

    return row_data


# namedtuple to match the internal signature of urlunparse
Components = namedtuple(
    typename='Components', 
    field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment']
)

html_files = glob.glob("gazettes.uk.gov.in/showgrid*.html")

# Step 7: Create a list to store all rows across all files
output_data = []

# Define the CSV file header
header = [
    "GO No.",
    "GO Date",
    "GO Description",
    "Issued by",
    "Gazette Week Date",
    "Pg No",
]

# incomplete_links = []

# def start_js_scrape(url):

def parse_html(html):
    # Step 3: Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html5lib")

    # Step 4: Extract the id=Datagrid1 table element
    table = soup.find("table", {"id": "Datagrid1"})

    # Step 5: Select all tr child elements and slice to exclude the first and last element
    tr_elements = table.find_all("tr")[1:-1]

    # Step 6: Extract and convert td elements to text, creating tuples for each row
    rows = []
    for tr in tr_elements:
        td_elements = tr.find_all("td")
        row_data = [td.get_text(strip=True) for td in td_elements]

        # Pre-process the row_data
        processed_row = preprocess_row_data(row_data)
        rows.append(tuple(processed_row))

    target = extract_target(table)
    form = gen_form(soup, target) if target else None

    return (rows,form)

def gen_form(soup, target):
    inputs = soup.find_all("input")
    data = {}
    for input in inputs:
        data[input.get("name")] = input.get("value")
    data["__EVENTTARGET"] = target
    del data['Button1']
    return data

def extract_target(table):
    target = None
    links_row = table.find_all("tr")[-1]
    current = links_row.find("span")
    for link in current.find_next_siblings('a'):
        if link.get_text(strip=True).strip().isdigit():
            target = link["href"].split("'")[1]
            break
    return target

def file_to_url(filename):
    parsed_url = urlparse(filename)
    url = urlunparse(
        Components(
            scheme='https',
            netloc='gazettes.uk.gov.in',
            query=path.splitext(parsed_url.query)[0],
            path='',
            url='/showgrid.aspx',
            fragment=''
        )
    )
    return url

def iter_html(html):
    rows,form = parse_html(html)
    yield rows

    # If we need to paginate this section
    if form:
        url = file_to_url(file)
        t = form['__EVENTTARGET']
        response = http.request_encode_body('POST', url, fields=form, encode_multipart=False)

        yield from iter_html(response.data)

http = urllib3.PoolManager()
# Step 2: Iterate through each HTML file
for file in html_files:
    print(f"Processing {file}")
    with open(file, "r", encoding="utf-8") as html:
        for rows in iter_html(html):
            output_data.extend(rows)

# Sort the final list by the fifth column (Gazette Week Date)
output_data.sort(key=lambda x: x[4])

# Step 8: Dump the final output list into a CSV file
with open("gazette_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(output_data)

print("CSV file 'gazette_data.csv' has been created.")
