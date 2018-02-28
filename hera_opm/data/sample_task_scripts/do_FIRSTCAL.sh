#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn=$(basename $1 uv)

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)
    nopol_base=$(remove_pol $fn)
    metrics_f=`echo ${nopol_base}HH.uv.ant_metrics.json`
    # assume optional second argument is location of ex_ants file
    if [ "$#" -gt 1 ]; then
	exants=$(prep_exants ${2})
    else
	exants=$(query_exants_db)
    fi
    echo firstcal_run.py --metrics_json=$metrics_f --ex_ants=${exants} --pol=$pol ${fn}HH.uv
    firstcal_run.py --metrics_json=$metrics_f --ex_ants=${exants} --pol=$pol ${fn}HH.uv
fi
