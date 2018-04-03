#!/bin/bash
set -e

# import common funcitons
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - directory of bad_ants files, with filename `{JD}.txt`
fn="${1}"
bad_ants_dir="${2}"

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)

    # get ant_metrics filename
    nopol_base=$(remove_pol ${fn})
    metrics_f=`echo ${nopol_base}.ant_metrics.json`

    # assume second argument is location of ex_ants folder
    # extract JD from filename
    jd=$(get_jd ${fn})

    # use awk to round off fractional bit
    jd_int=`echo $jd | awk '{$1=int($1)}1'`

    # make filename
    bad_ants_fn=`echo "${bad_ants_dir}/${jd_int}.txt"`
    exants=$(prep_exants ${bad_ants_fn})

    # run the command
    echo firstcal_run.py --overwrite --ex_ants=${exants} --metrics_json=${metrics_f} --pol=$pol ${fn}
    firstcal_run.py --overwrite --ex_ants=${exants} --metrics_json=${metrics_f} --pol=$pol ${fn}
fi
