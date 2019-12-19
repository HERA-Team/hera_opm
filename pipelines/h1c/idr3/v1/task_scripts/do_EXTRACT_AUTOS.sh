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

# get outfilename, removing extension and appending .autos.uvh5
autos_file=`echo ${uvh5_fn%.*}.autos.uvh5`

echo extract_autos.py ${uvh5_fn} ${autos_file} --clobber
extract_autos.py ${uvh5_fn} ${autos_file} --clobber
