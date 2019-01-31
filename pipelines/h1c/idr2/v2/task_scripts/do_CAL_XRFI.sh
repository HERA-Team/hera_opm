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
# 2 - metrics_ext
# 3 - flags_ext
# 4 - kt_size
# 5 - kf_size
# 6 - sig_init
# 7 - sig_adj
# 8 - freq_threshold
# 9 - time_treshold
# 10 - ex_ants_path

# Get list of bad ants
jd=$(get_jd ${bn})
jd_int=`echo $jd | awk '{$1=int($1)}1'`
bad_ants_fn=`echo "${2}/${jd_int}.txt"`
ex_ants=$(prep_exants ${bad_ants_fn})

omni_calfits_file=`echo ${fn%.*}.omni.calfits`
abs_calfits_file=`echo ${fn%.*}.abs.calfits`
model_file=`echo ${fn%.*}.omni_vis.uvh5`

echo cal_xrfi_run.py --omni_calfits_file=${omni_calfits_file} --abs_calfits_file=${abs_calfits_file} --model_file=${model_file} --metrics_ext=${2} --flag_ext=${3} --kt_size=${4} --kf_size=${5} --sig_init=${6} --sig_adj=${7} --freq_threshold=${8} --time_threshold=${9} --ex_ants=${ex_ants}
cal_xrfi_run.py --omni_calfits_file=${omni_calfits_file} --abs_calfits_file=${abs_calfits_file} --model_file=${model_file} --metrics_ext=${2} --flag_ext=${3} --kt_size=${4} --kf_size=${5} --sig_init=${6} --sig_adj=${7} --freq_threshold=${8} --time_threshold=${9} --ex_ants=${ex_ants}
