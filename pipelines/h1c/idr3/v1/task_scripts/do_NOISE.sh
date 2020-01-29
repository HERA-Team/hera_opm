#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
fn="${1}"

# make sure input file is correct uvh5 file
uvh5_fn=$(remove_pol $fn)
uvh5_fn=${uvh5_fn%.uv}.uvh5

# get outfilename, removing extension and appending .noise_std.uvh5
noise_file=`echo ${uvh5_fn%.*}.noise_std.uvh5`

# get appropriate smoothed calibration to apply
smooth_cal=`echo ${uvh5_fn%.*}.smooth_abs.calfits`

echo noise_from_autos.py ${uvh5_fn} ${noise_file} --calfile ${smooth_cal} --clobber
noise_from_autos.py ${uvh5_fn} ${noise_file} --calfile ${smooth_cal} --clobber
