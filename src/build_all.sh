#!/bin/bash
(
    set -e
    
    python3 -u Flares.py --timestamp 20190101000000 --first 2019-01-01 --last 2019-06-01
    python3 -u Flares.py --timestamp 20190601000000 --first 2019-06-01 --last 2020-01-01
    python3 -u Flares.py --timestamp 20200101000000 --first 2020-01-01 --last 2020-06-01
    python3 -u Flares.py --timestamp 20200601000000 --first 2020-06-01 --last 2021-01-01
    python3 -u Flares.py 
) 2>&1|tee build_all.log
