#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# get base filename
fn=$(basename $1 uv)

pol1="xx"
pol2="yy"
pol3="xy"
pol4="yx"

# get raw visibility waterfalls
base_xx=$(replace_pol ${fn} ${pol1})
base_yy=$(replace_pol ${fn} ${pol2})
base_xy=$(replace_pol ${fn} ${pol3})
base_yx=$(replace_pol ${fn} ${pol4})

wf_xx=`echo ${base_xx}HH.uvO.flags.npz`
wf_yy=`echo ${base_yy}HH.uvO.flags.npz`
wf_xy=`echo ${base_xy}HH.uvO.flags.npz`
wf_yx=`echo ${base_yx}HH.uvO.flags.npz`

# get model vis waterfall
nopol_base=$(remove_pol ${fn})
vis_wf=`echo ${nopol_base}HH.uv.vis.uvfits.flags.npz`

# get chisq waterfall
chi_wf=`echo ${nopol_base}HH.uv.omni.calfits.x.flags.npz`

# get gains waterfall
g_wf=`echo ${nopol_base}HH.uv.omni.calfits.g.flags.npz`

# make big list of waterfalls
wf_list=$(join_by , ${wf_xx} ${wf_yy} ${wf_xy} ${wf_yx} ${vis_wf} ${chi_wf} ${g_wf})

# build xrfi_apply commmand
echo xrfi_apply.py --infile_format=miriad --outfile_format=miriad --extension=R --overwrite --waterfalls=${wf_list} --flag_file=${fn}HH.uvO.flags.npz ${fn}HH.uvO
xrfi_apply.py --infile_format=miriad --outfile_format=miriad --extension=R --overwrite --waterfalls=${wf_list} --flag_file=${fn}HH.uvO.flags.npz ${fn}HH.uvO
