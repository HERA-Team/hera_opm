#!/bin/bash
set -e

# import common funcitons
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### adjacent filenames
# 2 - previous filename, if available (otherwise "None")
# 3 - subsequent filename, if available (otherwise "None")
### cal smoothing parameters - see hera_cal.smooth_cal for details
# 4 - time_scale
# 5 - mirror_sigmas
# 6 - freq_scale
# 7 - tol
# 8 - window
# 9 - skip_wgt
# 10 - maxiter

fn="${1}"
time_scale="${4}"
mirror_sigmas="${5}"
freq_scale="${6}"
tol="${7}"
window="${8}"
skip_wgt="${9}"
maxiter="${10}"

# we only want to run calibration smoothing on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)

    # make name of associated calfile for data file and output
    calfile=`echo ${fn}.abs.calfits`
    outfile=`echo ${fn}.smooth_abs.calfits`

    # assume second and third arguments are previous and next basename files
    prev_fn=${2}
    next_fn=${3}

    # make arguments for associated cal files and data files
    if [ ${prev_fn} != "None" ]; then
	prev_fn=$(replace_pol ${prev_fn} ${pol})
        prev_data=`echo --prev_data ${prev_fn}OCR`
        prev_cal=`echo --prev_cal ${prev_fn}.abs.calfits`
    else
        prev_data=""
        prev_cal=""
    fi
    if [ ${next_fn} != "None" ]; then
	next_fn=$(replace_pol ${next_fn} ${pol})
        next_data=`echo --next_data ${next_fn}OCR`
        next_cal=`echo --next_cal ${next_fn}.abs.calfits`
    else
        next_cal=""
        next_data=""
    fi

    echo smooth_cal_run.py ${calfile} ${fn}OCR ${outfile} --filetype miriad --clobber ${prev_cal} ${prev_data} ${next_cal} ${next_data} --time_scale ${time_scale} --mirror_sigmas ${mirror_sigmas} --freq_scale ${freq_scale} --tol ${tol} --window ${window} --skip_wgt ${skip_wgt} --maxiter ${maxiter}
    smooth_cal_run.py ${calfile} ${fn}OCR ${outfile} --filetype miriad --clobber ${prev_cal} ${prev_data} ${next_cal} ${next_data} --time_scale ${time_scale} --mirror_sigmas ${mirror_sigmas} --freq_scale ${freq_scale} --tol ${tol} --window ${window} --skip_wgt ${skip_wgt} --maxiter ${maxiter}
fi
