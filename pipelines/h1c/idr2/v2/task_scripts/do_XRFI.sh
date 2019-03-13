#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh
fn="${1}"  # Filename
bn=$(basename ${1})  # Basename

# We need to run xrfi on calibration outputs as preliminary flags before we
# delay filter and run xrfi on visibilities.

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### XRFI parameters - see hera_qm.utils for details
# 2 - init_metrics_ext
# 3 - init_flags_ext
# 4 - final_metrics_ext
# 5 - final_flags_ext
# 6 - kt_size
# 7 - kf_size
# 8 - sig_init
# 9 - sig_adj
# 10 - freq_threshold
# 11 - time_treshold

ocalfits_file=`echo ${fn%.*}.omni.calfits`
acalfits_file=`echo ${fn%.*}.abs.calfits`
model_file=`echo ${fn%.*}.omni_vis.uvh5`

echo xrfi_run.py --ocalfits_file=${omni_calfits_file} --acalfits_file=${abs_calfits_file} --model_file=${model_file} --data_file=${fn} --init_metrics_ext=${2} --init_flags_ext=${3} --final_metrics_ext=${4} --final_flags_ext=${5} --kt_size=${6} --kf_size=${7} --sig_init=${8} --sig_adj=${9} --freq_threshold=${10} --time_threshold=${11}
xrfi_run.py --ocalfits_file=${omni_calfits_file} --acalfits_file=${abs_calfits_file} --model_file=${model_file} --data_file=${fn} --init_metrics_ext=${2} --init_flags_ext=${3} --final_metrics_ext=${4} --final_flags_ext=${5} --kt_size=${6} --kf_size=${7} --sig_init=${8} --sig_adj=${9} --freq_threshold=${10} --time_threshold=${11}
