#!/bin/bash
set -e

# import common funcitons
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn="${1}"

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)

    # make name of associated calfile for data file and output
    calfile=`echo ${fn}.abs.calfits`
    outfile=`echo ${fn}.smooth_abs.calfits`

    # assume second and third arguments are previous and next basename files
    prev_fn=${2}
    next_fn=${3}

    # make name of associated cal files
    if [ ${prev_fn} != "None" ]; then
	prev_cal=`echo ${prev_fn}.abs.calfits`
    else
	prev_cal="None"
    fi
    if [ ${next_fn} != "None" ]; then
	next_cal=`echo ${next_nf}.abs.calfits`
    else
	next_cal="None"
    fi

    echo smooth_cal_run.py ${calfile} ${fn} ${outfile} --filetype=miriad --clobber --prev_cal=${prev_cal} \
	 --prev_data=${prev_fn} --next_cal=${next_cal} --next_data=${next_fn} --time_scale=120. --mirror_sigmas=5. \
	 --tol=1e-9
    smooth_cal_run.py ${calfile} ${fn} ${outfile} --filetype=miriad --clobber --prev_cal=${prev_cal} \
	 --prev_data=${prev_fn} --next_cal=${next_cal} --next_data=${next_fn} --time_scale=120. --mirror_sigmas=5. \
	 --tol=1e-9
fi
