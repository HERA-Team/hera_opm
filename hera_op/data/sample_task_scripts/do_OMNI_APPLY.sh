#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=$(basename $1 uv)

# get polarization
pol=$(get_pol $fn)

# get the name of the omnical file
nopol_base=$(remove_pol $fn)
omni_f=`echo ${nopol_base}HH.uv.omni.calfits`

echo omni_apply.py -p $pol --omnipath=$omni_f --extension=O --overwrite ${fn}HH.uv
omni_apply.py -p $pol --omnipath=$omni_f --extension=O --overwrite ${fn}HH.uv
