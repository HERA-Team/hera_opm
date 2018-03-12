#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=${1}

if is_lin_pol ${fn}; then
    # we only need the corresponding omnical solution
    omni_fn=`echo ${fn}.omni.calfits`

    echo apply_cal.py ${fn} ${fn}O --new_cal ${omni_fn} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn} ${fn}O --new_cal ${omni_fn} --clobber --filetype=miriad --gain_convention=divide
else
    # we need both omnical solutions
    fn_xx=$(replace_pol $fn "xx")
    fn_yy=$(replace_pol $fn "yy")
    omni_xx=`echo ${fn_xx}.omni.calfits`
    omni_yy=`echo ${fn_yy}.omni.calfits`

    echo apply_cal.py ${fn} ${fn}O --new_cal ${omni_xx} ${omni_yy} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn} ${fn}O --new_cal ${omni_fn} ${omni_yy} --clobber --filetype=miriad --gain_convention=divide
fi
