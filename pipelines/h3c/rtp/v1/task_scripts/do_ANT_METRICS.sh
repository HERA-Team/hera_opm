#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consisten wtih the config.
# 1 - (raw) filename
fn=$(inject_hh ${1})

# define polarizations
pol1="xx"
pol2="yy"
pol3="xy"
pol4="yx"

# make comma-separated list of polarizations
pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

echo ant_metrics_run.py -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.hdf5 --vis_format=uvh5 $fn
ant_metrics_run.py -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.hdf5 --vis_format=uvh5 $fn
