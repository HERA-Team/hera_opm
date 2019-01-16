#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - data filename
# 2 - data & model filetype
# 3 - glob-parsable string pointing to model_files
# 4 - integer maximum number of iterations of phase calibration algorithms allowed
# 5 - float convergence criterion in Delta g / g for stopping iterative phase_slope_cal or TT_phs_cal
# 6 - reference antenna for phase solvers
# 7 - maximum baseline length to use in calibration
# 8 - number of channels on each edge of bandpass to flag before delay calibration
# 9 - solar altitude above which data are flagged
# 10 - fraction of flagged visibilities, above which antenna gain is flagged
fn="${1}"
ft="${2}"
model_files="${3}"
phs_max_iter="${4}"
phs_conv_crit="${5}"
refant="${6}"
max_bl_cut="${7}"
edge_cut="${8}"
solar_horizon="${8}"
antflag_thresh="${10}"

# make calfits file name
omni_fn=`echo ${fn}.omni.calfits`
calfits_fn=`echo ${fn}.abs.calfits`

# call omni-abscal script; see hera_cal.abscal for more details
echo omni_abscal_run.py --refant ${refant} --max_bl_cut ${max_bl_cut} --edge_cut ${edge_cut} --solar_horizon ${solar_horizon} --antflag_thresh ${antflag_thresh} --avg_dly_slope_cal --delay_slope_cal --phase_slope_cal --TT_phs_cal --abs_amp_cal --phs_max_iter ${phs_max_iter} --phs_conv_crit ${phs_conv_crit} --overwrite --input_cal ${omni_fn} --output_calfits_fname ${calfits_fn} --data_file ${fn} --filetype ${ft} --model_files ${model_files} 
omni_abscal_run.py --refant ${refant} --max_bl_cut ${max_bl_cut} --edge_cut ${edge_cut} --solar_horizon ${solar_horizon} --antflag_thresh ${antflag_thresh} --avg_dly_slope_cal --delay_slope_cal --phase_slope_cal --TT_phs_cal --abs_amp_cal --phs_max_iter ${phs_max_iter} --phs_conv_crit ${phs_conv_crit} --overwrite --input_cal ${omni_fn} --output_calfits_fname ${calfits_fn} --data_file ${fn} --filetype ${ft} --model_files ${model_files} 
