#!/bin/bash

# This script downloads all valid gazette files
# by brute-forcing all valid filenames (=date.pdf)

start_date="01 JAN 2006"
current_date=$(date +"%d %b %Y")

# Create a function to download Gazette files
download_gazette() {
    formatted_date=$(date -d "$1" +"%d%m%y")
    dir="pdfs/20$(date -d "$1" +"%y/%m")"
    url="https://gazettes.uk.gov.in/entry/gazette/gz$formatted_date.pdf"
    mkdir -p "$dir"
    wget -q -nc -nv "$url" -O "$dir/$formatted_date.pdf"
}

# Export the function so GNU Parallel can access it
export -f download_gazette

# Generate a list of dates to download Gazette files
dates_to_download=()
while [ "$start_date" != "$current_date" ]; do
    dates_to_download+=("$start_date")
    start_date=$(date -d "$start_date + 1 day" +"%d %b %Y")
done

# Use GNU Parallel to download Gazette files in parallel
parallel -j 100 download_gazette ::: "${dates_to_download[@]}"

find . -type f -empty -delete
find . -type d -empty -delete

# Now, we need to download the information files (HTML)
# that contain the metadata for each Gazette file
wget -i input.txt  --recursive --adjust-extension --level 1 --ignore-tags=img,link  --relative --no-parent

# Now, we parse the metadata from the HTML files
# and save it as a CSV file
# in some cases, this will make a few further requests
python generate.py