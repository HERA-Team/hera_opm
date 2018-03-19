#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - glob-parsable string pointing to model_files
fn="${1}"
model_files="${2}"

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
    echo omni_abscal_run.py --delay_slope_cal --TT_phs_cal --abs_amp_cal --overwrite --calfits_infiles ${omni_fn} --output_calfits_fname ${calfits_fn} --data_files ${omni_data} --model_files ${model_files}
    omni_abscal_run.py --delay_slope_cal --TT_phs_cal --abs_amp_cal --overwrite --calfits_infiles ${omni_fn} --output_calfits_fname ${calfits_fn} --data_files ${omni_data} --model_files ${model_files}
fi
