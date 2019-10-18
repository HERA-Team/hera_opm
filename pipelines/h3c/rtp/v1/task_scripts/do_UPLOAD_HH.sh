#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consisten wtih the config.
# 1 - filename
fn="${1}"

# get the integer portion of the JD
jd=$(get_int_jd ${fn})

# make the name of the output file based on the input file
# we put "HH" immediately after the JD
fn_hh=`basename $fn | sed -E "s/(zen.[0-9]{7}\.[0-9]{5}\.)/\1HH./g"`

echo upload_to_librarian.py local-rtp ${fn_hh} ${jd}/${fn_hh}
librarian upload local-rtp ${fn_hh} ${jd}/${fn_hh}
