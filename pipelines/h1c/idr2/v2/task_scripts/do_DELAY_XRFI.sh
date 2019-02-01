#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh
fn="${1}"  # Filename
bn=$(basename ${1})  # Basename

# We run a delay filter, then xrfi on the data visibilities for all polarizations.
# We assume xrfi has already been run on the model visibilities, abscal gains/chisq,
# and omnical gains/chisq values. These flags are applied to the data before the
# delay filter in delay_xrfi_run.py.

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config. See hera_qm.utils for details.
# 1 - filename
### Delay filter parameters
# 2 - standoff
# 3 - horizon
# 4 - tol
# 5 - window
# 6 - skip_wgt
# 7 - maxiter
# 8 - alpha
## XRFI parameters
# 9 - metrics_ext
# 10 - flags_ext
# 11 - cal_ext
# 12 - kt_size
# 13 - kf_size
# 14 - sig_init
# 15 - sig_adj
# 16 - freq_threshold
# 17 - time_threshold
# 18 - bad_ants_dir

cal_metrics=`echo ${fn%.*}.cal_xrfi_metrics.h5`
cal_flags=`echo ${fn%.*}.cal_flags.h5`
input_cal=`echo ${fn%.*}.abs.calfits`

# Run on visibilities
echo delay_xrfi_run.py --input_cal=${input_cal} --standoff=${2} --horizon=${3} --tol=${4} --window=${5} --skip_wgt=${6} --maxiter=${7} --alpha=${8} --metrics_ext=${9} --flags_ext=${10} --cal_ext=${11} --kt_size=${12} --kf_size=${13} --sig_init=${14} --sig_adj=${15} --freq_threshold=${16} --time_threshold=${17} ${fn} ${cal_metrics} ${cal_flags}
delay_xrfi_run.py --input_cal=${input_cal} --standoff=${2} --horizon=${3} --tol=${4} --window=${5} --skip_wgt=${6} --maxiter=${7} --alpha=${8} --metrics_ext=${9} --flags_ext=${10} --cal_ext=${11} --kt_size=${12} --kf_size=${13} --sig_init=${14} --sig_adj=${15} --freq_threshold=${16} --time_threshold=${17} ${fn} ${cal_metrics} ${cal_flags}
