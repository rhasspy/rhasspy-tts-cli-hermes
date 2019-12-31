#!/usr/bin/env bash

url="$1"
lang="$2"
text="$3"

if [[ -z "${text}" ]]; then
    echo "Usage: marytts.sh URL LOCALE TEXT"
    exit 1
fi

curl -sS -X GET -G \
     --data-urlencode "INPUT_TEXT=${text}" \
     --data-urlencode "LOCALE=${lang}" \
     --data-urlencode 'INPUT_TYPE=TEXT' \
     --data-urlencode 'OUTPUT_TYPE=AUDIO' \
     --data-urlencode 'AUDIO=WAVE' \
     "${url}" \
     --output -
