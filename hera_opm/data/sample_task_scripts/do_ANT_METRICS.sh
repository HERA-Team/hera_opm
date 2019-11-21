#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# run script from hera_qm
fn=$(basename $1 uv)

# define polarizations
pol1="xx"
pol2="yy"
pol3="xy"
pol4="yx"

# we only want to run this script for the "xx" thread
if is_same_pol $fn $pol1; then
    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

    # make new filenames for polarizations
    fn1=$(replace_pol $fn $pol1)
    fn2=$(replace_pol $fn $pol2)
    fn3=$(replace_pol $fn $pol3)
    fn4=$(replace_pol $fn $pol4)

    echo ant_metrics_run.py -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.json --vis_format=miriad ${fn1}HH.uv ${fn2}HH.uv ${fn3}HH.uv ${fn4}HH.uv
    ant_metrics_run.py -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.json --vis_format=miriad ${fn1}HH.uv ${fn2}HH.uv ${fn3}HH.uv ${fn4}HH.uv
fi
