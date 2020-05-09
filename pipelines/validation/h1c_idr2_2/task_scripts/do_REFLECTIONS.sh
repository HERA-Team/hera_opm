#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
#  1 - data filename
#  2 - delay ranges
#  3 - fft window
#  4 - fft window alpha
#  5 - clean tolerance
#  6 - clean gain
#  7 - clean maxiter
#  8 - clean skip weight value
#  9 - fft edgecut low
# 10 - fft edgecut hi
# 11 - fft zeropad
# 12 - clean minimum delay
# 13 - time average before clean
# 14 - reflection optimization maxiter: 0 is no optimization
# 15 - reflection optimization method
# 16 - reflection optimization tolerance
filename="${1}"
dly_ranges="${2}"
window="${3}"
alpha="${4}"
tol="${5}"
gain="${6}"
maxiter="${7}"
skip_wgt="${8}"
edgecut_low="${9}"
edgecut_hi="${10}"
zeropad="${11}"
min_dly="${12}"
time_avg="${13}"
opt_maxiter="${14}"
opt_method="${15}"
opt_tol="${16}"

# parse time_avg
if [ ${time_avg} == "True" ]
then
    time_avg="--time_avg"
else
    time_avg=""
fi

# get input and output calibration filenames
input_cal=`echo ${filename%.uvh5}.smooth_abs.calfits`
output_fname=`echo ${filename%.uvh5}.reflections.calfits`

# run auto_reflection_run.py
echo auto_reflection_run.py ${filename} --dly_ranges ${dly_ranges} --output_fname ${output_fname} --filetype uvh5 --overwrite --write_npz --input_cal ${input_cal} ${time_avg} --window ${window} --alpha ${alpha} --tol ${tol} --gain ${gain} --maxiter ${maxiter} --skip_wgt ${skip_wgt} --edgecut_low ${edgecut_low} --edgecut_hi ${edgecut_hi} --zeropad ${zeropad} --min_dly ${min_dly} --opt_maxiter ${opt_maxiter} --opt_method ${opt_method} --opt_tol ${opt_tol}
auto_reflection_run.py ${filename} --dly_ranges ${dly_ranges} --output_fname ${output_fname} --filetype uvh5 --overwrite --write_npz --input_cal ${input_cal} ${time_avg} --window ${window} --alpha ${alpha} --tol ${tol} --gain ${gain} --maxiter ${maxiter} --skip_wgt ${skip_wgt} --edgecut_low ${edgecut_low} --edgecut_hi ${edgecut_hi} --zeropad ${zeropad} --min_dly ${min_dly} --opt_maxiter ${opt_maxiter} --opt_method ${opt_method} --opt_tol ${opt_tol}
