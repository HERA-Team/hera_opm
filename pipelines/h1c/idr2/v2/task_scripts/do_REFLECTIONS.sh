#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
#  1 - data filename
#  2 - delay ranges
#  3 - input calibration
#  4 - fft window
#  5 - fft window alpha
#  6 - clean tolerance
#  7 - clean gain
#  8 - clean maxiter
#  9 - clean skip weight value
# 10 - fft edgecut low
# 11 - fft edgecut hi
# 12 - fft zeropad
# 13 - clean minimum delay
# 14 - time average before clean
# 15 - reflection optimization maxiter: 0 is no optimization
# 16 - reflection optimization method
# 17 - reflection optimization tolerance
filename="${1}"
dly_ranges="${2}"
input_cal="${3}"
window="${4}"
alpha="${5}"
tol="${6}"
gain="${7}"
maxiter="${8}"
skip_wgt="${9}"
edgecut_low="${10}"
edgecut_hi="${11}"
zeropad="${12}"
min_dly="${13}"
time_avg="${14}"
opt_maxiter="${15}"
opt_method="${16}"
opt_tol="${17}"

# parse time_avg
if [ ${time_avg} == 'True' ]
then
    time_avg="--time_avg"
else
    time_avg=""
fi

# get output filename
output_fname="${filename%.uvh5}.ref.calfits"

# parse input_cal
input_cal="${filename%.uvh5}.${input_cal}"

echo auto_reflection_run.py ${filename} --output_fname ${output_fname} --filetype uvh5 --overwrite --write_npz --input_cal ${input_cal} ${time_avg} --window ${window} --alpha ${alpha} --tol ${tol} --gain ${gain} --maxiter ${maxiter} --skip_wgt ${skip_wgt} --edgecut_low ${edgecut_low} --edgecut_hi ${edgecut_hi} --zeropad ${zeropad} --min_dly ${min_dly} --opt_maxiter ${opt_maxiter} --opt_method ${opt_method} --opt_tol ${opt_tol}
auto_reflection_run.py ${filename} --output_fname ${output_fname} --filetype uvh5 --overwrite --write_npz --input_cal ${input_cal} ${time_avg} --window ${window} --alpha ${alpha} --tol ${tol} --gain ${gain} --maxiter ${maxiter} --skip_wgt ${skip_wgt} --edgecut_low ${edgecut_low} --edgecut_hi ${edgecut_hi} --zeropad ${zeropad} --min_dly ${min_dly} --opt_maxiter ${opt_maxiter} --opt_method ${opt_method} --opt_tol ${opt_tol}
