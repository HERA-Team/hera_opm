#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define input arguments
fn="${1}"

# remove antmetrics
am_fn=$(remove_pol ${fn})
am_fn=${am_fn}.ant_metrics.json
echo rm -rfv ${am_fn}
rm -rfv ${am_fn}

# remove uvh5 files
uvh5_fn=$(remove_pol ${fn})
uvh5_fn=${uvh5_fn%.uv}.uvh5
echo rm -rfv ${uvh5_fn}
rm -rfv ${uvh5_fn}

# remove firstcal files
firstcal_fn=${uvh5_fn%.uvh5}.first.calfits
echo rm -rfv ${firstcal_fn}
rm -rfv ${firstcal_fn}

# remove unflagged abscal files
abscal_fn=${uvh5_fn%.uvh5}.abs.calfits
echo rm -rfv ${abscal_fn}
rm -rfv ${abscal_fn}