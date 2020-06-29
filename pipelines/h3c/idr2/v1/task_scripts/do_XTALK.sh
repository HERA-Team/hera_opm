#! /bin/bash
set -e

#import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - file name
# 2 - output label
# 3 - Level to subtract cross-talk too.
# 4 - First xtalk filter coefficient. Remove power below fringe-rates of fc0 * bl_len + fc1.
# 5 - Second xtalk filter coefficient. Remove power below fringe-rates of fc0 * bl_len + fc1
# 6 - Cache Directory.

fn="${1}"
label="${2}"
tol="${3}"
frc0="${4}"
frc1="${5}"
cache_dir="${6}"
# get julian day from file name
jd=$(get_jd $fn)
int_jd=${jd:0:7}
# generate output file name
fn=zen.${jd}.${label}.foreground_filtered.uvh5
fn_out=zen.${jd}.${label}.xtalk_filtered_waterfall.uvh5
# if cache directory does not exist, make it
if [ ! -d "${cache_dir}" ]; then
  mkdir ${cache_dir}
fi
# list of all foreground filtered files.
data_files=`echo zen.${int_jd}.*.${label}.foreground_filtered.uvh5`


echo xtalk_dayenu_filter_run_baseline_parallelized.py ${fn} --tol ${tol} \
 --max_frate_coeffs ${frc0} ${frc1} --cache_dir ${cache_dir} --res_outfilename ${fn_out} \
 --clobber --datafilelist ${data_files} #--write_cache --read_cache


 xtalk_dayenu_filter_run_baseline_parallelized.py ${fn} --tol ${tol} \
  --max_frate_coeffs ${frc0} ${frc1} --cache_dir ${cache_dir} --res_outfilename ${fn_out} \
  --clobber --datafilelist ${data_files} #--write_cache --read_cache
