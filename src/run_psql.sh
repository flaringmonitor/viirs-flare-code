#!/bin/bash
# shell script that uses local_settings.py as a source of it's psql
# connection string
ME=$(readlink -f "$0")
BASE=$(dirname "$ME")
psql "`python3 "$BASE"/local_settings.py`" $*
