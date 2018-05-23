#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Positional parameters passed as defined in the configuration file:
# 1 - base filename
# 2 - flag_nchan_low (n low frequency channels to flag)
# 3 - flag_nchan_high (n high frequency channels to flag)
# 4 - vis_units (string)
fn=${1}

if is_lin_pol ${fn}; then
    # we only need the corresponding omnical solution
    abs_fn=`echo ${fn}.abs.calfits`

    echo apply_cal.py ${fn} ${fn}OC --new_cal ${abs_fn} --flag_nchan_low=${2} --flag_nchan_high=${3} --clobber --filetype=miriad --gain_convention=divide --vis_units ${4}
    apply_cal.py ${fn} ${fn}OC --new_cal ${abs_fn} --flag_nchan_low=${2} --flag_nchan_high=${3} --clobber --filetype=miriad --gain_convention=divide --vis_units ${4}
else
    # we need both omnical solutions
    fn_xx=$(replace_pol $fn "xx")
    fn_yy=$(replace_pol $fn "yy")
    abs_xx=`echo ${fn_xx}.abs.calfits`
    abs_yy=`echo ${fn_yy}.abs.calfits`

    echo apply_cal.py ${fn} ${fn}OC --new_cal ${abs_xx} ${abs_yy} --flag_nchan_low=${2} --flag_nchan_high=${3} --clobber --filetype=miriad --gain_convention=divide --vis_units ${4}
    apply_cal.py ${fn} ${fn}OC --new_cal ${abs_xx} ${abs_yy} --flag_nchan_low=${2} --flag_nchan_high=${3} --clobber --filetype=miriad --gain_convention=divide --vis_units ${4}
fi
