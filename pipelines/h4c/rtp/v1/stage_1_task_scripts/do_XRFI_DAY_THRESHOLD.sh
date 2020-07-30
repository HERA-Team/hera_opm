#! /bin/bash
set -e

# This script performs daylong thresholding on xrfi results

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

echo xrfi_day_threshold_run.py ${data_files} --skip_making_flagged_abs_calfits --nsig_f=${1} --nsig_t=${2} --nsig_f_adj=${3} --nsig_t_adj=${4} --clobber
xrfi_day_threshold_run.py ${data_files} --skip_making_flagged_abs_calfits --nsig_f=${1} --nsig_t=${2} --nsig_f_adj=${3} --nsig_t_adj=${4} --clobber

# Rename results so that there will be no conflict with stage 2
if [ $? == 0 ]; then
    for df in ${data_files}; do
        echo mv ${df%.sum.uvh5}.xrfi  ${df%.sum.uvh5}.stage_1_xrfi
        mv ${df%.sum.uvh5}.xrfi ${df%.sum.uvh5}.stage_1_xrfi
    done
    for ff in *_threshold_flags.h5; do
        echo mv ${ff} ${ff%_threshold_flags.h5}_stage_1_threshold_flags.h5
        mv ${ff} ${ff%_threshold_flags.h5}_stage_1_threshold_flags.h5
    done
fi
