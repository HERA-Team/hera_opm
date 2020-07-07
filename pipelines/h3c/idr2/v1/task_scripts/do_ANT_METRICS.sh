#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consisten wtih the config.
# 1 - (raw) filename
# 2 - crossCut: Modified z-score cut for most cross-polarized antenna.
# 3 - deadCut: Modified z-score cut for most likely dead antenna.
# 4 - extension: Extension to be appended to the file name.
# 5 - vis_format: File format for visibility files.
fn=${1}
crossCut=${2}
deadCut=${3}
extension=${4}
vis_format=${5}

# define polarizations
pol1="nn"
pol2="ee"
pol3="ne"
pol4="en"

# make comma-separated list of polarizations
pols=$(join_by , $pol1 $pol2 $pol3 $pol4)
# We only want to run ant metrics on sum files
echo ant_metrics_run.py -p $pols --crossCut=${crossCut} --deadCut=${deadCut} --extension=${extension} --vis_format=${vis_format} $fn
ant_metrics_run.py -p $pols --crossCut=${crossCut} --deadCut=${deadCut} --extension=${extension} --vis_format=${vis_format} $fn
