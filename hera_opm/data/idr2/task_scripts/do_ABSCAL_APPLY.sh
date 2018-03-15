#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=${1}

if is_lin_pol ${fn}; then
    # we only need the corresponding omnical solution
    abs_fn=`echo ${fn}.abs.calfits`

    echo apply_cal.py ${fn}O ${fn}OC --new_cal ${abs_fn} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn}O ${fn}OC --new_cal ${abs_fn} --clobber --filetype=miriad --gain_convention=divide
else
    # we need both omnical solutions
    fn_xx=$(replace_pol $fn "xx")
    fn_yy=$(replace_pol $fn "yy")
    abs_xx=`echo ${fn_xx}.abs.calfits`
    abs_yy=`echo ${fn_yy}.abs.calfits`

    echo apply_cal.py ${fn}O ${fn}OC --new_cal ${abs_xx} ${abs_yy} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn}O ${fn}OC --new_cal ${abs_xx} ${abs_yy} --clobber --filetype=miriad --gain_convention=divide
fi
