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
# 7 - vis_units
# 8 - output_file_select
# 9 - file_ext
# 10 - outdir
# 11+ - series of glob-parsable search strings (in quotations!) to files to LSTBIN

# get positional arguments
sig_clip=${1}
sigma=${2}
min_N=${3}
rephase=${4}
ntimes_per_file=${5}
lst_start=${6}
vis_units=${7}
output_file_select=${8}
file_ext=${9}
outdir=${10}
data_files=($@)
data_files=(${data_files[*]:10})

# set special kwargs
if [ $sig_clip == True ]; then
    sig_clip="--sig_clip"
else
    sig_clip=""
fi
if [ $rephase == True ]; then
    rephase="--rephase"
else
    rephase=""
fi

echo lstbin_run.py --file_ext ${file_ext} --outdir ${outdir} --ntimes_per_file ${ntimes_per_file} ${sig_clip} --sigma ${sigma} --min_N ${min_N} --lst_start ${lst_start} --vis_units ${vis_units} --output_file_select ${output_file_select} --overwrite ${data_files[@]}
lstbin_run.py --file_ext ${file_ext} --outdir ${outdir} --ntimes_per_file ${ntimes_per_file} ${sig_clip} --sigma ${sigma} --min_N ${min_N} --lst_start ${lst_start} --vis_units ${vis_units} --output_file_select ${output_file_select} --overwrite ${data_files[@]}
