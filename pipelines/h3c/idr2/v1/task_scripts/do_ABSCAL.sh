#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - data filename
# 2 - glob-parsable string pointing to model_files
# 3 - integer number of integrations to load and calibrate simultaneously
# 3 - float minimum baseline length to use in calibration
# 4 - float maximum baseline length to use in calibration
# 5 - integer maximum number of iterations of phase calibration algorithms allowed
# 6 - float convergence criterion for updates to iterative phase calibration
# 7 - number of channels on each edge of bandpass to flag before delay calibration
fn="${1}"
model_files="${2}"
nInt_to_load="${3}"
min_bl_cut="${4}"
max_bl_cut="${5}"
phs_max_iter="${6}"
phs_conv_crit="${7}"
edge_cut="${8}"

# make calfits file name
omni_fn=`echo ${fn%.*}.omni.calfits`

# call omni-abscal script; see hera_cal.abscal for more details
echo post_redcal_abscal_run.py ${fn} ${omni_fn} ${model_files} --nInt_to_load ${nInt_to_load} --min_bl_cut ${min_bl_cut} --max_bl_cut ${max_bl_cut} \
                               --phs_max_iter ${phs_max_iter} --phs_conv_crit ${phs_conv_crit} --edge_cut ${edge_cut} --model_is_redundant --clobber --verbose
post_redcal_abscal_run.py ${fn} ${omni_fn} ${model_files} --nInt_to_load ${nInt_to_load} --min_bl_cut ${min_bl_cut} --max_bl_cut ${max_bl_cut} \
                          --phs_max_iter ${phs_max_iter} --phs_conv_crit ${phs_conv_crit} --edge_cut ${edge_cut} --model_is_redundant --clobber --verbose
