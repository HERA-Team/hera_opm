#! /bin/bash

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - calibration file
# 3 - number of baselines to partially load and filter
#     at a time
# 4 - extra label for the output file.
# 5 - spw0 lower channel to process.
# 6 - spw1 upper channel to process.
# 7 - tol level to subtract foregrounds too
# 8 - standoff delay standoff in ns for filtering window
# 9 - cache_dir, directory to store cache files in.
fn="${1}"
calibration="${2}"
nbls_partial="${3}"
output_label="${4}"
spw0="${5}"
spw1="${6}"
tol="${7}"
standoff="${8}"
cache_dir="${9}"
# get julian day from file name
jd=$(get_jd ${fn})
# generate output file name
fn_out = ${jd}.${output_label}.dayenu_delay_resid.ch${spw0}_${spw1}.uvh5
# if cache directory does not exist, make it
if [ ! -d "${cache_dir}" ]; then
  mkdir ${cache_dir}
fi
cal_file="${filename%.uvh5}.${calibration}"

echo dayenu_delay_filter_run.py --calfile ${calfile} --partial_load_Nbls ${nbls_partial} \
  --res_outfilename ${fn_out} --clobber --spw_range ${spw0} ${spw1} \
  --tol ${tol} --cache_dir ${cache_dir} --standoff ${standoff}

dayenu_delay_filter_run.py --calfile ${calfile} --partial_load_Nbls ${nbls_partial} \
    --res_outfilename ${fn_out} --clobber --spw_range ${spw0} ${spw1} \
    --tol ${tol} --cache_dir ${cache_dir} --standoff ${standoff}
