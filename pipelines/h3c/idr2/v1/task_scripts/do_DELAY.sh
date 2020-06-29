#! /bin/bash
set -e

#import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - calibration file
# 3 - extra label for the output file.
# 4 - spw0 lower channel to process.
# 5 - spw1 upper channel to process.
# 6 - tol level to subtract foregrounds too
# 7 - standoff delay standoff in ns for filtering window.
# 8 - cache_dir, directory to store cache files in.
fn="${1}"
calibration="${2}"
label="${3}"
spw0="${4}"
spw1="${5}"
tol="${6}"
standoff="${7}"
cache_dir="${8}"
# get julian day from file name
jd=$(get_jd $fn)
# generate output file name
fn_out=zen.${jd}.${label}.foreground_filtered.uvh5
# if cache directory does not exist, make it
if [ ! -d "${cache_dir}" ]; then
  mkdir ${cache_dir}
fi
calfile=${fn%.uvh5}.${calibration}

echo dayenu_delay_filter_run.py ${fn} --calfile ${calfile} \
  --res_outfilename ${fn_out} --clobber --spw_range ${spw0} ${spw1} \
  --tol ${tol} --cache_dir ${cache_dir} --standoff ${standoff} #--write_cache --read_cache

dayenu_delay_filter_run.py ${fn} --calfile ${calfile} \
    --res_outfilename ${fn_out} --clobber --spw_range ${spw0} ${spw1} \
    --tol ${tol} --cache_dir ${cache_dir} --standoff ${standoff} #--write_cache --read_cache
