#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn="${1}"
calfile=`echo ${fn%.*}.first.calfits`


echo firstcal_metrics_run.py ${metrics_f}
firstcal_metrics_run.py ${metrics_f}
