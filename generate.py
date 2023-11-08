import glob
import csv
from bs4 import BeautifulSoup
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


html_files = glob.glob("gazettes.uk.gov.in/showgrid*.html")

# Step 7: Create a list to store all rows across all files
output_data = []

# Define the CSV file header
header = ["GO No.", "GO Date", "GO Description", "Issued by", "Gazette Week Date", "Pg No"]

# Step 2: Iterate through each HTML file
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        # Step 3: Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(f, 'html5lib')

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

        # Extend the output_data list with the rows from the current file
        output_data.extend(rows)

# Sort the final list by the fifth column (Gazette Week Date)
output_data.sort(key=lambda x: x[4])

# Step 8: Dump the final output list into a CSV file
with open("gazette_data.csv", 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write the header
    writer.writerow(header)
    
    # Write the data
    writer.writerows(output_data)

print("CSV file 'gazette_data.csv' has been created.")
