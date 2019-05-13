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
# 9 - freq_threshold
# 10 - time_threshold
# 11 - ant_threshold

fn="${1}"
freq_scale="${2}"
time_scale="${3}"
tol="${4}"
filter_mode="${5}"
window="${6}"
maxiter="${7}"
alpha="${8}"
freq_threshold="${9}"
time_threshold="${10}"
ant_threshold="${11}"

# get list of all calfiles for a day
jd=$(get_jd $fn)
int_jd=${jd:0:7}
calfiles=`echo zen.${int_jd}.*.flagged_abs.calfits`

# make the name of this calfits file for --run_if_first option
this_calfile=`echo ${fn%.*}.flagged_abs.calfits`

echo smooth_cal_run.py ${calfiles} --infile_replace .flagged_abs. --outfile_replace .smooth_abs. --clobber \
                  --pick_refant --run_if_first ${this_calfile} --freq_scale ${freq_scale} \
                  --time_scale ${time_scale} --tol ${tol} --filter_mode ${filter_mode} --window ${window} \
                  --maxiter ${maxiter} --alpha ${alpha} --freq_threshold ${freq_threshold} \
                  --time_threshold ${time_threshold} --ant_threshold ${ant_threshold} --verbose
smooth_cal_run.py ${calfiles} --infile_replace .flagged_abs. --outfile_replace .smooth_abs. --clobber \
                  --pick_refant --run_if_first ${this_calfile} --freq_scale ${freq_scale} \
                  --time_scale ${time_scale} --tol ${tol} --filter_mode ${filter_mode} --window ${window} \
                  --maxiter ${maxiter} --alpha ${alpha} --freq_threshold ${freq_threshold} \
                  --time_threshold ${time_threshold} --ant_threshold ${ant_threshold} --verbose
