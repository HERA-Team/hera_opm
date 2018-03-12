#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=${1}

# make name of flags file
flags_npz=`echo ${fn}OCR.flags.applied.npz`

if is_lin_pol ${fn}; then
    # we only need the corresponding omnical solution
    smoothcal_fn=`echo ${fn}.smooth_abs.calfits`

    echo apply_cal.py ${fn}OCR ${fn}OCRS --new_cal ${smoothcal_fn} --flags_npz=${flags_npz} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn}OCR ${fn}OCRS --new_cal ${smoothcal_fn} --flags_npz=${flags_npz} --clobber --filetype=miriad --gain_convention=divide
else
    # we need both omnical solutions
    fn_xx=$(replace_pol $fn "xx")
    fn_yy=$(replace_pol $fn "yy")
    smoothcal_xx=`echo ${fn_xx}.abs.calfits`
    smoothcal_yy=`echo ${fn_yy}.abs.calfits`

    echo apply_cal.py ${fn}OCR ${fn}OCRS --new_cal ${smoothcal_xx} ${smoothcal_yy} --flags_npz=${flags_npz} --clobber --filetype=miriad --gain_convention=divide
    apply_cal.py ${fn}OCR ${fn}OCRS --new_cal ${smoothcal_fn} ${smoothcal_yy} --flags_npz=${flags_npz} --clobber --filetype=miriad --gain_convention=divide
fi
