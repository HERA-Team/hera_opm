#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
fn="${1}"

# Use xrfi_transfer.py to bring over flags from H1C IDR2.2
echo python ${src_dir}/xrfi_transfer.py ${fn}
python ${src_dir}/xrfi_transfer.py ${fn}
