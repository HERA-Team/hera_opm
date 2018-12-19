#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn="${1}"

# we only run omnical metrics on linear polarization threads
if is_lin_pol $fn; then
    # get firstcal file name
    fcal=`echo ${fn}.first.calfits`

    # get omnical file name
    omni_fn=`echo ${fn}.omni.calfits`

    # call python script
    echo omnical_metrics_run.py --fc_files=${fcal} ${omni_fn}
    omnical_metrics_run.py --fc_files=${fcal} ${omni_fn}
fi
