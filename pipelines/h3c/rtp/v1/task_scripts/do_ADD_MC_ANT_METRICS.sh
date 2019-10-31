#!/bin/bash
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

# get ant_metrics filename
metrics_f="${fn%.*}"${extension}
echo add_qm_metrics.py --type=ant ${metrics_f}
add_qm_metrics.py --type=ant ${metrics_f}
