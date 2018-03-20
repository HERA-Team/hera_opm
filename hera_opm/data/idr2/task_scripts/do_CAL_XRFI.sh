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
# which must be consistent with the config.
# 1 - filename
# 2 - bad_ants_dir
### XRFI parameters - see hera_qm.utils for details
# 3 - kt_size
# 4 - kf_size
# 5 - sig_init
# 6 - sig_adj
# 7 - px_threshold
# 8 - freq_threshold
# 9 - time_threshold

# Get list of bad ants
jd=$(get_jd ${bn})
jd_int=`echo $jd | awk '{$1=int($1)}1'`
bad_ants_fn=`echo "${2}/${jd_int}.txt"`
exants=$(prep_exants ${bad_ants_fn})

if is_lin_pol ${bn}; then
    # This thread runs on model vis
    # get the name of the model vis file
    vis_f=`echo ${bn}.vis.uvfits`

    # run the xrfi command
    echo xrfi_run.py --kt_size=${3} --kf_size=${4} --sig_init=${5} --sig_adj=${6} --px_threshold=${7} --freq_threshold=${8} --time_threshold=${9} --exants=${exants} --model_file=${vis_f} --model_file_format=uvfits --algorithm=xrfi --extension=.flags.npz
    xrfi_run.py --kt_size=${3} --kf_size=${4} --sig_init=${5} --sig_adj=${6} --px_threshold=${7} --freq_threshold=${8} --time_threshold=${9} --exants=${exants} --model_file=${vis_f} --model_file_format=uvfits --algorithm=xrfi --extension=.flags.npz
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
    echo xrfi_run.py --kt_size=${3} --kf_size=${4} --sig_init=${5} --sig_adj=${6} --px_threshold=${7} --freq_threshold=${8} --time_threshold=${9} --exants=${exants} --calfits_file=${abs_f} --algorithm=xrfi --extension=.flags.npz
    xrfi_run.py --kt_size=${3} --kf_size=${4} --sig_init=${5} --sig_adj=${6} --px_threshold=${7} --freq_threshold=${8} --time_threshold=${9} --exants=${exants} --calfits_file=${abs_f} --algorithm=xrfi --extension=.flags.npz
fi
