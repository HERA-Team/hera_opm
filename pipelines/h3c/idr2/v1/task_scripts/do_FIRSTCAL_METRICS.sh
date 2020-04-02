#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

fn="${1}"

calfile=`echo ${fn%.*}.first.calfits`

echo firstcal_metrics_run.py --clobber ${calfile}
firstcal_metrics_run.py --clobber ${calfile}
