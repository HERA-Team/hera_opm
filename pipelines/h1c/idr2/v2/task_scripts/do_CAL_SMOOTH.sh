#!/bin/bash
set -e

# import common funcitons
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### cal smoothing parameters - see hera_cal.smooth_cal for details
# 2 - freq_scale
# 3 - time_scale
# 4 - tol
# 5 - filter_mode
# 6 - window
# 7 - maxiter
# 8 - alpha
# 9 - antflag_thresh

fn="${1}"
freq_scale="${2}"
time_scale="${3}"
tol="${4}"
filter_mode="${5}"
window="${6}"
maxiter="${7}"
alpha="${8}"
antflag_thresh="${9}"

# get list of all calfiles for a day
jd=$(get_jd $fn)
int_jd=${jd:0:7}
calfiles=`echo zen.${int_jd}.*.flagged_abs.calfits`

# make the name of this calfits file for --run_if_first option
this_calfile=`echo ${fn%.*}.flagged_abs.calfits`

echo smooth_cal_run.py ${calfiles} --infile_replace .flagged_abs. --outfile_replace .smooth_abs. --clobber --antflag_thresh ${antflag_thresh} \
                  --pick_refant --run_if_first ${this_calfile} --time_scale ${time_scale} --freq_scale ${freq_scale} --tol ${tol} \
                  --filter_mode ${filter_mode} --window ${window} --maxiter ${maxiter} --alpha ${alpha} --verbose
smooth_cal_run.py ${calfiles} --infile_replace .flagged_abs. --outfile_replace .smooth_abs. --clobber --antflag_thresh ${antflag_thresh} \
                  --pick_refant --run_if_first ${this_calfile} --time_scale ${time_scale} --freq_scale ${freq_scale} --tol ${tol} \
                  --filter_mode ${filter_mode} --window ${window} --maxiter ${maxiter} --alpha ${alpha} --verbose
