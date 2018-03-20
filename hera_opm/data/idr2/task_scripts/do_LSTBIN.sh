#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - sig_clip flag
# 2 - sigma threshold
# 3 - min_N threshold
# 4 - rephase flag
# 5 - ntimes_per_file
# 6 - lst_start
# 7+ - series of glob-parsable search strings (in quotations!) to files to LSTBIN

# get positional arguments
sig_clip=${1}
sigma=${2}
min_N=${3}
rephase=${4}
ntimes_per_file=${5}
lst_start=${6}
data_files=($@)
data_files=(${data_files[*]:6})

# we only want to run on linear polarizations (e.g., "xx")
if is_lin_pol $fn; then
    echo lstbin_run.py --ntimes_per_file ${ntimes_per_file} --overwrite ${sig_clip} --sigma ${sigma} --min_N ${min_N} --lst_start ${lst_start} ${data_files}
    lstbin_run.py --ntimes_per_file ${ntimes_per_file} --overwrite ${sig_clip} --sigma ${sigma} --min_N ${min_N} --lst_start ${lst_start} ${data_files}
fi
