#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Positional parameters passed as defined in the configuration file:
# 1 - base filename
# 2 - flag_nchan_low (n low frequency channels to flag)
# 3 - flag_nchan_high (n high frequency channels to flag)
fn=${1}

if is_lin_pol ${fn}; then
    # we only need the corresponding omnical solution
    omni_fn=`echo ${fn}.omni.calfits`

    echo apply_cal.py ${fn} ${fn}O --new_cal ${omni_fn} --clobber --flag_nchan_low=${2} --flag_nchan_high=${3} --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn} ${fn}O --new_cal ${omni_fn} --clobber --flag_nchan_low=${2} --flag_nchan_high=${3} --filetype=miriad --gain_convention=divide
else
    # we need both omnical solutions
    fn_xx=$(replace_pol $fn "xx")
    fn_yy=$(replace_pol $fn "yy")
    omni_xx=`echo ${fn_xx}.omni.calfits`
    omni_yy=`echo ${fn_yy}.omni.calfits`

    echo apply_cal.py ${fn} ${fn}O --new_cal ${omni_xx} ${omni_yy} --flag_nchan_low=${2} --flag_nchan_high=${3} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn} ${fn}O --new_cal ${omni_xx} ${omni_yy} --flag_nchan_low=${2} --flag_nchan_high=${3} --clobber --filetype=miriad --gain_convention=divide
fi
