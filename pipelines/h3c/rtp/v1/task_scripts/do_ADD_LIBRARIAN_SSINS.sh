#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consistent wtih the config.
# 1 - (raw) filename
fn=${1}

# get the integer portion of the JD
jd=$(get_int_jd ${1})

midfix=".SSINS."
prefix="${fn%.*}"${midfix}

# make a new directory
dirname="${prefix::-1}"
mkdir "$dirname"

for suffix in data.h5 z_score.h5 mask.h5 flags.h5 match_events.yml; do
  file=${prefix}${suffix}
  mv $file $dirname
done

echo librarian upload local-rtp $dirname ${jd}/$dirname
librarian upload local-rtp $dirname ${jd}/$dirname
