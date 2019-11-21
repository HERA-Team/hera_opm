#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define input arguments
fn="${1}"

# combine all 4 polarizations into a single file using pyuvdata
fn_xx=${fn}
fn_yy=$(replace_pol $fn "yy")
fn_xy=$(replace_pol $fn "xy")
fn_yx=$(replace_pol $fn "yx")
fn_out=$(remove_pol $fn)
fn_out=${fn_out%.uv}.uvh5

# build python script as series of commands
echo python -c "from pyuvdata import UVData; uv = UVData(); uv.read([\"${fn_xx}\", \"${fn_yy}\", \"${fn_xy}\", \"${fn_yx}\"], axis=\"polarization\"); uv.x_orientation = 'east'; uv.history += '\n\nx_orientation manually set to east\n\n'; uv.write_uvh5(\"${fn_out}\", clobber=True)"
python -c "from pyuvdata import UVData; uv = UVData(); uv.read([\"${fn_xx}\", \"${fn_yy}\", \"${fn_xy}\", \"${fn_yx}\"], axis=\"polarization\"); uv.x_orientation = 'east'; uv.history += '\n\nx_orientation manually set to east\n\n'; uv.write_uvh5(\"${fn_out}\", clobber=True)"
