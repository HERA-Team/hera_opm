#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - directory of bad_ants files, with filename `{JD}.txt`
fn="${1}"
bad_ants_dir="${2}"

# define polarizations
pol1="xx"
pol2="yy"

# we run omnical on linear pols only
if is_lin_pol $fn; then
    # define polarization file names
    fn1=$(replace_pol $fn $pol1)
    fn2=$(replace_pol $fn $pol2)

    # get firstcal file names
    # should be auto-pol (e.g., 'xx')
    declare -a FCAL_ARR
    idx=0
    for f in $fn1 $fn2; do
        # test if file is a linear polarization
        if is_lin_pol $f; then
            # add to array
            file_pol=$(get_pol $f)
            FCAL_ARR[$idx]=$file_pol
            idx=$((idx+1))
        fi
    done

    # make list of firstcal files by iterating over array values
    idx=0
    for pol in "${FCAL_ARR[@]}"; do
        base=$(replace_pol $fn $pol)
        FCAL_ARR[$idx]=`echo ${base}.first.calfits`
        idx=$((idx+1))
    done

    # make comma-separated list of firstcal files
    fcal=$(join_by , "${FCAL_ARR[@]}")

    # get current polarization
    pol=$(get_pol $fn)

    # get metrics_json filename
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

    echo omni_run.py --firstcal=$fcal --overwrite --ex_ants=${exants} --metrics_json=${metrics_f} -p $pol ${fn}
    omni_run.py --firstcal=$fcal --overwrite --ex_ants=${exants} --metrics_json=${metrics_f} -p $pol ${fn}
fi
