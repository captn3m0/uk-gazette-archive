#!/bin/bash

start_date="01 JAN 2006"
current_date=$(date +"%d %b %Y")

# Create a function to download Gazette files
download_gazette() {
    formatted_date=$(date -d "$1" +"%d%m%y")
    dir="pdfs/20$(date -d "$1" +"%y/%m")"
    url="https://gazettes.uk.gov.in/entry/gazette/gz$formatted_date.pdf"
    mkdir -p "$dir"
    wget -nc -nv "$url" -O "$dir/$formatted_date.pdf"
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