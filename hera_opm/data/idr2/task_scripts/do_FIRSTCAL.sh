#!/bin/bash
set -e

# import common funcitons
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn=$(basename $1 uv)

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)

    # assume optional second argument is location of ex_ants file
    if [ "$#" -gt 1 ]; then
        exants=$(prep_exants ${2})
    else
        exants=$(query_exants_db)
    fi
    echo firstcal_run.py --ex_ants=${exants} --pol=$pol ${fn}uv
    firstcal_run.py --ex_ants=${exants} --pol=$pol ${fn}uv
fi
