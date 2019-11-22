#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consistent with the config.
# 1 - raw filename
# 2 - the significance threshold for streak shapes
# 3 - the significance threshold to use for the other shapes
fn=${1}
streak_sig=${2}
other_sig=${3}
N_samp_thresh=${4}

# Get the right raw file
prefix="${fn%.*}"

echo Run_HERA_SSINS.py -f $fn -s $streak_sig -o $other_sig -p prefix -N N_samp_thresh
Run_HERA_SSINS.py -f $fn -s $streak_sig -o $other_sig -p prefix -N N_samp_thresh
