#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=$(basename $1)

pol1="xx"
pol2="yy"
pol3="xy"
pol4="yx"

# This script will take in all the waterfalls produced by the various DELAY_XRFI
# threads, union them, and apply to the data. It will produce a flagged data file
# and an npz file with the flag array for this data set.

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
# 2 - extension
# 3 - output_npz_ext

# get raw visibility waterfalls
base_xx=$(replace_pol ${fn} ${pol1})
base_yy=$(replace_pol ${fn} ${pol2})
base_xy=$(replace_pol ${fn} ${pol3})
base_yx=$(replace_pol ${fn} ${pol4})

wf_xx=`echo ${base_xx}OC.flags.npz`
wf_yy=`echo ${base_yy}OC.flags.npz`
wf_xy=`echo ${base_xy}OC.flags.npz`
wf_yx=`echo ${base_yx}OC.flags.npz`

# get model vis waterfall
vis_wf_xx=`echo ${base_xx}.vis.uvfits.flags.npz`
vis_wf_yy=`echo ${base_yy}.vis.uvfits.flags.npz`

# get chisq waterfall
chi_wf_xx=`echo ${base_xx}.abs.calfits.x.flags.npz`
chi_wf_yy=`echo ${base_yy}.abs.calfits.x.flags.npz`

# get gains waterfall
g_wf_xx=`echo ${base_xx}.abs.calfits.g.flags.npz`
g_wf_yy=`echo ${base_yy}.abs.calfits.g.flags.npz`

# make big list of waterfalls
wf_list=$(join_by , ${wf_xx} ${wf_yy} ${wf_xy} ${wf_yx} ${vis_wf_xx} ${vis_wf_yy} ${chi_wf_xx} ${chi_wf_yy} ${g_wf_xx} ${g_wf_yy})

# build xrfi_apply commmand
echo xrfi_apply.py --extension=${2} --overwrite --out_npz_ext=${3} --waterfalls=${wf_list} ${fn}OC
xrfi_apply.py --extension=${2} --overwrite --out_npz_ext=${3} --waterfalls=${wf_list} ${fn}OC
