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

# get the name of the diff file
fn_diff=$(inject_diff ${fn})

echo librarian upload local-rtp ${fn} ${jd}/${fn}
librarian upload local-rtp ${fn} ${jd}/${fn}
echo librarian upload local-rtp ${fn_diff} ${jd}/${fn_diff}
librarian upload local-rtp ${fn_diff} ${jd}/${fn_diff}
