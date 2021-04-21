#!/bin/bash
set -e

ME=$(readlink -f "$0")
BASE=$(dirname "$ME")
DATA="$BASE/../../viirs-flare-data/csv"

cd "$BASE/csv"

# if we don't already have uncompressed CSV files, uncompress
# don't overwrite manual updates of CSV files

for i in *.sql
do
    base=`basename "$i" .sql`
    csv="$base.csv"
    gz="$csv.gz"
    echo "Uncompressing $gz"
    gunzip <"$DATA/$gz" >"$csv"
    echo "Loading $csv"
    ../run_psql.sh -f "$i"
done

echo "Loads complete"
