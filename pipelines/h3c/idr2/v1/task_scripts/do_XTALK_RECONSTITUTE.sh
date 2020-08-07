#! /bin/bash
set -e

#import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# This script reconstitutes as time chunk from many baselines.
# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - template file name (template for time chunk to reconstitute).
# 2 - output label for identifying file.

templatefile="${1}"
label="${2}"

jd=$(get_jd $templatefile)
int_jd=${jd:0:7}
# generate output file name
outfilename=zen.${jd}.${label}.xtalk_filtered.uvh5

fragment_list=`echo zen.${int_jd}.*.${label}.xtalk_filtered_waterfall.uvh5`

echo reconstitute_xtalk_filtered_files_run.py ${templatefile} --outfilename ${outfilename}\
    --fragmentlist ${fragment_list}

reconstitute_xtalk_filtered_files_run.py ${templatefile} --outfilename ${outfilename}\
    --fragmentlist ${fragment_list}
