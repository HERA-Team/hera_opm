#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
fn="${1}"

# get outfilename, removing extension and appending .noise_std.uvh5
noise_file=`echo ${fn%.*}.noise_std.uvh5`

# get appropriate smoothed calibration to apply
smooth_cal=`echo ${fn%.*}.smooth_abs.calfits`

echo noise_from_autos.py ${fn} ${noise_file} --calfile ${smooth_cal} --clobber
noise_from_autos.py ${fn} ${noise_file} --calfile ${smooth_cal} --clobber
