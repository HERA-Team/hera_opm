#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=$(basename $1 uv)

# we only want to run on linear polarizations (e.g., "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)

    # assume optional second argument is location of ex_ants file
    exants=$(prep_exants ${2})

    echo abscal_run.py --ex_ants=${exants} --pol=${pol} ${fn}uv
    abscal_run.py --ex_ants=${exants} --pol=${pol} ${fn}uv
fi
