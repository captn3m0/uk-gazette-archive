#!/bin/bash

# Define the parent directory
parent_dir="./"

# Loop through second-level directories and create zip files
for dir in "$parent_dir"*/; do
    if [ -d "$dir" ] && [ ! -e "${dir}.*" ]; then
        base_dir=$(basename "$dir")
        zip_file_name="${base_dir}.zip"
        echo zip -r "$zip_file_name" "$dir"
    fi
done