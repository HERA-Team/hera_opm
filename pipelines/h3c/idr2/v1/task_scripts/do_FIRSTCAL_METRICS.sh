#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn="${1}"

# make sure input file is correct uvh5 file
uvh5_fn=$(remove_pol $fn)
uvh5_fn=${uvh5_fn%.uv}.uvh5

calfile=`echo ${uvh5_fn%.*}.first.calfits`

echo firstcal_metrics_run.py --clobber ${calfile}
firstcal_metrics_run.py --clobber ${calfile}
