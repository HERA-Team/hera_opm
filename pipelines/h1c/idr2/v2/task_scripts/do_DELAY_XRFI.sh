#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh
fn="${1}"  # Filename
bn=$(basename ${1})  # Basename

# We run a delay filter, then xrfi on the data visibilities for all polarizations.
# We assume xrfi has already been run on the model visibilities, abscal gains/chisq,
# and omnical gains/chisq values. These flags are applied to the data before the
# delay filter in delay_xrfi_run.py.

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config. See hera_qm.utils for details.
# 1 - filename
### Delay filter parameters
# 2 - standoff
# 3 - horizon
# 4 - tol
# 5 - window
# 6 - skip_wgt
# 7 - maxiter
# 8 - alpha
## XRFI parameters
# 9 - metrics_ext
# 10 - flags_ext
# 11 - cal_ext
# 12 - kt_size
# 13 - kf_size
# 14 - sig_init
# 15 - sig_adj
# 16 - freq_threshold
# 17 - time_threshold
# 18 - bad_ants_dir

# Get list of bad ants
jd=$(get_jd ${bn})
jd_int=`echo $jd | awk '{$1=int($1)}1'`
bad_ants_fn=`echo "${2}/${jd_int}.txt"`
ex_ants=$(prep_exants ${bad_ants_fn})

cal_metrics=`echo ${fn%.*}.cal_metrics.h5`
cal_flags=`echo ${fn%.*}.cal_flags.h5`
input_cal=`echo ${fn%.*}.abs.calfits`

xrfi.xrfi_h1c_run(args.vis_file, args.cal_metrics, args.cal_flags, history,
                  input_cal=args.input_cal, standoff=args.standoff, horizon=args.horizon,
                  tol=args.tol, window=args.window, skip_wgt=args.skip_wgt,
                  maxiter=args.maxiter, alpha=args.alpha, metrics_ext=args.metrics_ext,
                  flags_ext=args.flags_ext, cal_ext=args.cal_ext, kt_size=args.kt_size,
                  kf_size=args.kf_size, sig_init=args.sig_init, sig_adj=args.sig_adj,
                  freq_threshold=args.freq_threshold, time_threshold=args.time_threshold,
                  ex_ants=args.ex_ants, metrics_file=args.metrics_file)


# Run on visibilities
echo delay_xrfi_run.py --vis_file=${fn} --cal_metrics=${cal_metrics} --cal_flags=${cal_flags} --input_cal=${input_cal} --standoff=${2} --horizon=${3} --tol=${4} --window=${5} --skip_wgt=${6} --maxiter=${7} --alpha=${8} --metrics_ext=${9} --flags_ext=${10} --cal_ext=${11} --kt_size=${12} --kf_size=${13} --sig_init=${14} --sig_adj=${15} --freq_threshold=${16} --time_threshold=${17} --ex_ants=${ex_ants}
delay_xrfi_run.py --vis_file=${fn} --cal_metrics=${cal_metrics} --cal_flags=${cal_flags} --input_cal=${input_cal} --standoff=${2} --horizon=${3} --tol=${4} --window=${5} --skip_wgt=${6} --maxiter=${7} --alpha=${8} --metrics_ext=${9} --flags_ext=${10} --cal_ext=${11} --kt_size=${12} --kf_size=${13} --sig_init=${14} --sig_adj=${15} --freq_threshold=${16} --time_threshold=${17} --ex_ants=${ex_ants}
