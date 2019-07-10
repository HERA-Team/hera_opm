#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### XRFI parameters - see hera_qm.utils for details
# 2 - kt_size
# 3 - kf_size
# 4 - nsig_f
# 5 - nsig_t

fn="${1}"
data_files=`echo ${fn%.*}.uvh5`

echo xrfi_day_threshold_run.py ${data_files} --kt_size=${2} --kf_size=${3} --nsig_f=${4} --nsig_t=${5} --run_if_first --clobber ${fn}
xrfi_day_threshold_run.py ${data_files} --kt_size=${2} --kf_size=${3} --nsig_f=${4} --nsig_t=${5} --run_if_first --clobber ${fn}
