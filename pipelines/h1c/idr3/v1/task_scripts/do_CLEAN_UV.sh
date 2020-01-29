#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define input arguments
fn="${1}"

# remove raw miriad files
fn_xx=${fn}
fn_yy=$(replace_pol $fn "yy")
fn_xy=$(replace_pol $fn "xy")
fn_yx=$(replace_pol $fn "yx")
echo rm -rf "${fn_xx}"
rm -rf "${fn_xx}"
echo rm -rf "${fn_yy}"
rm -rf "${fn_yy}"
echo rm -rf "${fn_xy}"
rm -rf "${fn_xy}"
echo rm -rf "${fn_yx}"
rm -rf "${fn_yx}"
