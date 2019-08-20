#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define input arguments
fn="${1}"

# remove uvh5 files
uvh5_fn=$(remove_pol ${fn})
uvh5_fn=${uvh5_fn%.uv}.uvh5
echo rm -rf ${uvh5_fn}
rm -rf ${uvh5_fn}
