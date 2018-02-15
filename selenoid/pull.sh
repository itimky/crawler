#!/usr/bin/env bash

declare -a ARR=(
    'selenoid/chrome:latest'
    'selenoid/chrome:64.0'
    'selenoid/chrome:63.0'
    'selenoid/chrome:62.0'
    'selenoid/chrome:61.0'
    'selenoid/chrome:60.0'

    'selenoid/firefox:latest'
    'selenoid/firefox:58.0'
    'selenoid/firefox:57.0'
)

printf "%s\n" ${ARR[*]} | xargs -l docker pull


