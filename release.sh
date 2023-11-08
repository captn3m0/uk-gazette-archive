#!/bin/bash

find "pdfs" -mindepth 2 -maxdepth 2 -type d \! -name ".*" -exec sh -c 'base_dir=$(basename "$1"); year=$(basename "$(dirname "$1")"); month=$(basename "$1"); if [ ${#month} -eq 1 ]; then month="0$month"; fi; zip -r "releases/${year}-${month}.zip" "$1"' _ {} \;