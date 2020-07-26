#! /bin/bash
set -e

# This script downselects data for the purpose transfering via internet. TODO: this currently does nothing!

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - (raw) filename
fn=${1}

echo "THIS IS A PLACEHOLDER FOR THE IMAGING PIPELINE DOWNSELECT. NOT CURRENTLY IMPLEMENTED."

echo "THIS IS A PLACEHOLDER FOR THE BISPECTRUM / DELAY SPECTRUM PIPELINE DOWNSELECT. NOT CURRENTLY IMPLEMENTED."
