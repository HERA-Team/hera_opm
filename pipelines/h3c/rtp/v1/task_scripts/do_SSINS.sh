#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consistent with the config.

# 1 - the significance threshold for streak shapes
# 2 - the significance threshold to use for the other shapes
# 3 - The threshold for flagging a highly contaminated frequency channel
# 4 - The filename(s) to read in

streak_sig=${1}
other_sig=${2}
N_samp_thresh=${3}
fn=${4}

# Get the first filename in the list (should work if only one file)
first_file="${fn%" "*}"
# Set the prefix based on the first filename
prefix="${first_file%.*}"

echo Run_HERA_SSINS.py -f $fn -s $streak_sig -o $other_sig -p $prefix -N $N_samp_thresh -c
Run_HERA_SSINS.py -f $fn -s $streak_sig -o $other_sig -p $prefix -N $N_samp_thresh -c
