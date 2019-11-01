#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consisten wtih the config.
# 1 - (raw) filename
# 2 - extension: Extension to be appended to the file name.
fn=$(inject_hh ${1})
extension=${2}

# get the integer portion of the JD
jd=$(get_int_jd ${1})

# get ant_metrics filename
metrics_f="${fn%.*}"${extension}

echo upload_to_librarian.py local-rtp ${metrics_f} ${jd}/${metrics_f}
librarian upload local-rtp ${metrics_f} ${jd}/${metrics_f}