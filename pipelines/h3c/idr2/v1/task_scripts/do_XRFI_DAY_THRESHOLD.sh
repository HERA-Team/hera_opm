#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### XRFI parameters - see hera_qm.utils for details
# 2 - nsig_f
# 3 - nsig_t
# 4 - nsig_f_adj
# 5 - nsig_t_adj

fn="${1}"
# get list of all data files for a day

jd=$(get_jd $fn)
int_jd=${jd:0:7}
data_files=`echo zen.${int_jd}.*.sum.uvh5`

echo xrfi_day_threshold_run.py ${data_files} --nsig_f=${2} --nsig_t=${3} --nsig_f_adj=${4} --nsig_t_adj=${5} --clobber --run_if_first ${fn}
xrfi_day_threshold_run.py ${data_files} --nsig_f=${2} --nsig_t=${3} --nsig_f_adj=${4} --nsig_t_adj=${5} --clobber --run_if_first ${fn}
