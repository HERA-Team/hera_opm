#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# define polarizations
pol1="xx"
pol2="xy"
pol3="yy"
pol4="yx"

# make the file name
bn=$(basename ${1})
# Get pol
pol=$(get_pol ${1})

# We need to run xrfi on calibration outputs as preliminary flags before we
# delay filter and run xrfi on visibilities. We will take advantage of the cross-pol
# threads to handle all four files to flag on simultaneously:
# pol1 = xx -> xx.HH.uv.vis.uvfits (xx model visibilities)
# pol2 = xy -> xx.HH.uv.abs.calfits (xx gain solutions and chi-squareds)
# pol3 = yy -> yy.HH.uv.vis.uvfits (yy model visibilities)
# pol4 = yx -> yy.HH.uv.abs.calfits (yy gain solutions and chi-squareds)

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config. NOTE we do not pass the bad ants
# because they will not exist in the abs.calfits, and ant numbers are meaningless
# in model vis files.
# 1 - filename
### XRFI parameters - see hera_qm.utils for details
# 2 - kt_size
# 3 - kf_size
# 4 - sig_init
# 5 - sig_adj
# 6 - px_threshold
# 7 - freq_threshold
# 8 - time_threshold

if is_lin_pol ${bn}; then
    # This thread runs on model vis
    # get the name of the model vis file
    vis_f=`echo ${bn}.vis.uvfits`

    # run the xrfi command
    echo xrfi_run.py --kt_size=${2} --kf_size=${3} --sig_init=${4} --sig_adj=${5} --px_threshold=${6} --freq_threshold=${7} --time_threshold=${8} --model_file=${vis_f} --model_file_format=uvfits --algorithm=xrfi --extension=.flags.npz
    xrfi_run.py --kt_size=${2} --kf_size=${3} --sig_init=${4} --sig_adj=${5} --px_threshold=${6} --freq_threshold=${7} --time_threshold=${8} --model_file=${vis_f} --model_file_format=uvfits --algorithm=xrfi --extension=.flags.npz
else
    # These threads run on gains and chi-squareds
    # First switch to corresponding lin pol
    if [ ${pol} == ${pol2} ]; then
        pn=$(replace_pol ${bn} ${pol1})
    else
        pn=$(replace_pol ${bn} ${pol3})
    fi
    # get the name of the calfits file
    cal_f=`echo ${pn}.abs.calfits`
    echo xrfi_run.py --kt_size=${2} --kf_size=${3} --sig_init=${4} --sig_adj=${5} --px_threshold=${6} --freq_threshold=${7} --time_threshold=${8} --calfits_file=${cal_f} --algorithm=xrfi --extension=.flags.npz
    xrfi_run.py --kt_size=${2} --kf_size=${3} --sig_init=${4} --sig_adj=${5} --px_threshold=${6} --freq_threshold=${7} --time_threshold=${8} --calfits_file=${cal_f} --algorithm=xrfi --extension=.flags.npz
fi
