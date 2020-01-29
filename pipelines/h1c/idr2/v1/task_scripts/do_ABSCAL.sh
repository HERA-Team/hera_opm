#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - glob-parsable string pointing to model_files
# 3 - integer maximum number of iterations of phase calibration algorithms allowed
# 4 - float convergence criterion in Delta g / g for stopping iterative phase_slope_cal or TT_phs_cal
# 5 - reference antenna for phase solvers
# 6 - enact a cut on max baseline length for data that goes into calibration equations
# 7 - number of channels on each edge of bandpass to flag before delay calibration

fn="${1}"
model_files="${2}"
phs_max_iter="${3}"
phs_conv_crit="${4}"
refant="${5}"
bl_cut="${6}"
edge_cut="${7}"
solar_horizon="${8}"
antflag_thresh="${9}"

# we only want to run on linear polarizations (e.g., "xx")
if is_lin_pol $fn; then
    # make calfits file name
    omni_fn=`echo ${fn}.omni.calfits`
    calfits_fn=`echo ${fn}.abs.calfits`

    # substitute polarization of filename into model file list
    pol=$(get_pol ${fn})
    model_files=`echo ${model_files} | sed -E "s/\.pp\./.$pol./g"`

    # make filepath strings
    omni_data=${fn}O

    # call omni-abscal script; see hera_cal.abscal for more details
    echo omni_abscal_run.py --refant ${refant} --bl_cut ${bl_cut} --edge_cut ${edge_cut} --solar_horizon ${solar_horizon} --antflag_thresh ${antflag_thresh} --avg_dly_slope_cal --delay_slope_cal --phase_slope_cal --TT_phs_cal --abs_amp_cal --phs_max_iter ${phs_max_iter} --phs_conv_crit ${phs_conv_crit} --overwrite --calfits_infile ${omni_fn} --output_calfits_fname ${calfits_fn} --data_file ${omni_data} --model_files ${model_files}
    omni_abscal_run.py --refant ${refant} --bl_cut ${bl_cut} --edge_cut ${edge_cut} --solar_horizon ${solar_horizon} --antflag_thresh ${antflag_thresh} --avg_dly_slope_cal --delay_slope_cal --phase_slope_cal --TT_phs_cal --abs_amp_cal --phs_max_iter ${phs_max_iter} --phs_conv_crit ${phs_conv_crit} --overwrite --calfits_infile ${omni_fn} --output_calfits_fname ${calfits_fn} --data_file ${omni_data} --model_files ${model_files}
fi
