#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn=$(basename $1 uv)

# define polarizations
pol1="xx"
pol2="yy"

# we only run omnical for the base filename
if is_same_pol $fn $pol1; then
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
        FCAL_ARR[$idx]=`echo ${base}uv.first.calfits`
        idx=$((idx+1))
    done

    # make comma-separated list of firstcal files
    fcal=$(join_by , "${FCAL_ARR[@]}")

    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2)

    # assume optional second argument is location of ex_ants file
    if [ "$#" -gt 1 ]; then
        exants=$(prep_exants ${2})
    else
        exants=$(query_exants_db)
    fi

    echo omni_run.py --firstcal=$fcal --ex_ants=${exants} -p $pols ${fn1}uv ${fn2}uv
    omni_run.py --firstcal=$fcal --ex_ants=${exants} -p $pols ${fn1}uv ${fn2}uv
fi
