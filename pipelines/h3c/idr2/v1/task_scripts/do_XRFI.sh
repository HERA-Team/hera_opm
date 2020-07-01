#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh
data_files="${@:5}"

# We need to run xrfi on calibration outputs as preliminary flags before we
# delay filter and run xrfi on visibilities.

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
### XRFI parameters - see hera_qm.utils for details
# 1 - kt_size
# 2 - kf_size
# 3 - sig_init
# 4 - sig_adj
# 5+ - filenames

ocalfits_files=''
acalfits_files=''
model_files=''
for data_file in ${data_files[@]}; do
  # Append list of cal files
  ocalfits_files=${ocalfits_files}${data_file%.*}.omni.calfits' '
  acalfits_files=${acalfits_files}${data_file%.*}.abs.calfits' '
  model_files=${model_files}${data_file%.*}.omni_vis.uvh5' '
done

echo xrfi_h3c_idr2_1_run.py --ocalfits_files ${ocalfits_files} --acalfits_files ${acalfits_files} --model_files ${model_files} --data_files ${data_files} --kt_size=${1} --kf_size=${2} --sig_init=${3} --sig_adj=${4} --clobber
xrfi_h3c_idr2_1_run.py --ocalfits_files ${ocalfits_files} --acalfits_files ${acalfits_files} --model_files ${model_files} --data_files ${data_files} --kt_size=${1} --kf_size=${2} --sig_init=${3} --sig_adj=${4} --clobber
