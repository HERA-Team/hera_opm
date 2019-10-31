#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consisten wtih the config.
# 1 - filename
fn="${1}"

# make the name of the output file based on the input file
# we put "HH" immediately after the JD
fn_out=$(inject_hh ${fn})

echo extract_hh.py ${fn} ${fn_out}
extract_hh.py ${fn} ${fn_out}
