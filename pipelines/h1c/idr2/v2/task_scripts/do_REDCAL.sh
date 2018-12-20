#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - directory of bad_ants files, with filename `{JD}.txt`
# 3 - ant_z_thresh: Threshold of modified z-score for chi^2 per antenna above which antennas are thrown away and calibration is re-run iteratively.
# 4 - solar_horizon: When the Sun is above this altitude in degrees, calibration is skipped and the integrations are flagged.
# 5 - nInt_to_load: number of integrations to load and calibrate simultaneously. Lower numbers save memory, but incur a CPU overhead.
fn="${1}"
bad_ants_dir="${2}"
ant_z_thresh="${3}"
solar_horizon="${4}"
nInt_to_load="${5}"

# get metrics_json filename, removing extension and appending .ant_metrics.json
nopol_base=$(remove_pol ${fn})
metrics_f=`echo ${nopol_base%.*}.ant_metrics.json`

# assume second argument is location of ex_ants folder
# extract JD from filename
jd=$(get_jd ${fn})

# use awk to round off fractional bit
jd_int=`echo $jd | awk '{$1=int($1)}1'`

# make filename
bad_ants_fn=`echo "${bad_ants_dir}/${jd_int}.txt"`
exants=$(prep_exants ${bad_ants_fn})

echo redcal_run.py ${fn} --ex_ants=${exants} --ant_metrics_file=${metrics_f}  --ant_z_thresh=${ant_z_thresh} --solar_horizon=${solar_horizon} --nInt_to_load=${nInt_to_load} --clobber --verbose
redcal_run.py ${fn} --ex_ants=${exants} --ant_metrics_file=${metrics_f}  --ant_z_thresh=${ant_z_thresh} --solar_horizon=${solar_horizon} --nInt_to_load=${nInt_to_load} --clobber --verbose

