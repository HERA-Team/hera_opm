#!/bin/bash
set -e

# import common funcitons
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### cal smoothing parameters - see hera_cal.smooth_cal for details
# 2 - time_scale
# 3 - mirror_sigmas
# 4 - freq_scale
# 5 - tol
# 6 - window
# 7 - skip_wgt
# 8 - maxiter
# 9 - alpha
# 10 - antflag_thresh

fn="${1}"
time_scale="${2}"
mirror_sigmas="${3}"
freq_scale="${4}"
tol="${5}"
window="${6}"
skip_wgt="${7}"
maxiter="${8}"
alpha="${9}"
antflag_thresh="${10}"

# we only want to run calibration smoothing on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    pol=$(get_pol $fn)

    # make name of associated calfiles and flag files
    # get integer JD by extracting first 7 characters
    jd=$(get_jd $fn)
    int_jd=${jd:0:7}
    calfiles=`echo zen.${int_jd}.*.${pol}.*.abs.calfits`
    flagfiles=`echo zen.${int_jd}.*.${pol}.*.flags.applied.npz`

    # make the name of this calfits file for --run_if_first option
    this_calfile=`echo ${fn}.abs.calfits`

    echo smooth_cal_run.py ${calfiles} --flags_npz_list ${flagfiles} --infile_replace .abs. --outfile_replace .smooth_abs. --clobber --time_scale ${time_scale} --mirror_sigmas ${mirror_sigmas} --freq_scale ${freq_scale} --tol ${tol} --window ${window} --skip_wgt ${skip_wgt} --maxiter ${maxiter} --alpha ${alpha} --antflag_thresh ${antflag_thresh} --run_if_first ${this_calfile}
    smooth_cal_run.py ${calfiles} --flags_npz_list ${flagfiles} --infile_replace .abs. --outfile_replace .smooth_abs. --clobber --time_scale ${time_scale} --mirror_sigmas ${mirror_sigmas} --freq_scale ${freq_scale} --tol ${tol} --window ${window} --skip_wgt ${skip_wgt} --maxiter ${maxiter} --alpha ${alpha} --antflag_thresh ${antflag_thresh} --run_if_first ${this_calfile}
fi
