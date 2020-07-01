#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
### XRFI parameters - see hera_qm.utils for details
# 1 - nsig_f
# 2 - nsig_t
# 3 - nsig_f_adj
# 4 - nsig_t_adj
# 5+ - filenames

data_files="${@:5}"

echo xrfi_day_threshold_run.py --nsig_f=${1} --nsig_t=${2} --nsig_f_adj=${3} --nsig_t_adj=${4} --clobber ${data_files}
xrfi_day_threshold_run.py --nsig_f=${1} --nsig_t=${2} --nsig_f_adj=${3} --nsig_t_adj=${4} --clobber ${data_files}
