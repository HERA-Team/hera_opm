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
echo xrfi_apply.py --infile_format=miriad --outfile_format=miriad --extension=R --overwrite --output_npz --out_npz_ext=.flags.applied.npz --waterfalls=${wf_list} ${fn}OC
xrfi_apply.py --infile_format=miriad --outfile_format=miriad --extension=R --overwrite --output_npz --out_npz_ext=.flags.applied.npz --waterfalls=${wf_list} ${fn}OC
