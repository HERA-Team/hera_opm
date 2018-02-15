#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn=$(basename $1 uv)

# define polarizations
pol1="xx"
pol2="yy"

# we only run omnical metrics on a single polarization thread
if is_same_pol $fn $pol1; then
    # get firstcal file names
    base=$(replace_pol $fn $pol1)
    fcal_xx=`echo ${base}HH.uv.first.calfits`
    base=$(replace_pol $fn $pol2)
    fcal_yy=`echo ${base}HH.uv.first.calfits`

    # get omnical file name
    nopol_base=$(remove_pol $fn)
    omni_fn=`echo ${nopol_base}HH.uv.omni.calfits`

    # make a comma-separated list of firstcal files
    # XXX: current design limitation: YY must come before XX
    fcal=$(join_by , $fcal_yy $fcal_xx)

    # call python script
    echo omnical_metrics_run.py --fc_files=${fcal} ${omni_fn}
    omnical_metrics_run.py --fc_files=${fcal} ${omni_fn}
fi
