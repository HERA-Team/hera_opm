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
# 2 - kt_size
# 3 - kf_size
# 4 - sig_init
# 5 - sig_adj

ocalfits_file=`echo ${fn%.*}.omni.calfits`
acalfits_file=`echo ${fn%.*}.abs.calfits`
model_file=`echo ${fn%.*}.omni_vis.uvh5`

echo xrfi_run.py --ocalfits_file=${ocalfits_file} --acalfits_file=${acalfits_file} --model_file=${model_file} --data_file=${fn} --kt_size=${2} --kf_size=${3} --sig_init=${4} --sig_adj=${5} --clobber
xrfi_run.py --ocalfits_file=${ocalfits_file} --acalfits_file=${acalfits_file} --model_file=${model_file} --data_file=${fn} --kt_size=${2} --kf_size=${3} --sig_init=${4} --sig_adj=${5} --clobber
