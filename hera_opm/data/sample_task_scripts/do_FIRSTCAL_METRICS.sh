#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn=$(basename $1 uv)

# we only want to run firstcal on linear polarizations (e.g. "xx")
if is_lin_pol $fn; then
    metrics_f=`echo ${fn}HH.uv.first.calfits`
    echo firstcal_metrics_run.py --std_cut=0.5 --extension=.firstcal_metrics.json ${metrics_f}
    firstcal_metrics_run.py --std_cut=0.5 --extension=.firstcal_metrics.json ${metrics_f}
fi
