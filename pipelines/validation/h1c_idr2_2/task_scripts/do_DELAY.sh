#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename
### Delay filter parameters - see hera_cal.delay_filter for details
# 2 partial_load_Nbls
# 3 - standoff: fixed additional delay beyond the horizon (in ns)
# 4 - horizon: proportionality constant for bl_len where 1.0 is the horizon (full light travel time)
# 5 - tol: CLEAN algorithm convergence tolerance
# 6 - window: function for frequency filtering (see uvtools.dspec.gen_window for options)
# 7 - skip_wgt: skips filtering and flags times with unflagged fraction ~< skip_wgt
# 8 - maxiter: maximum iterations for aipy.deconv.clean to converge
# 9 - alpha: If window='tukey', use this alpha parameter
fn="${1}"
partial_load_Nbls="${2}"
standoff="${3}"
horizon="${4}"
tol="${5}"
window="${6}"
skip_wgt="${7}"
maxiter="${8}"
alpha="${9}"

# get delay filter residual outfilename
res_outfilename=`echo ${fn%.*}.OCRSD.uvh5`

# get appropriate smoothed calibration to apply
smooth_cal=`echo ${fn%.*}.smooth_abs.calfits`

# run the command
echo delay_filter_run.py ${fn} --calfile ${smooth_cal} --partial_load_Nbls ${partial_load_Nbls} --res_outfilename ${res_outfilename} --filetype_in uvh5 --filetype_out uvh5 --clobber --standoff ${standoff} --horizon ${horizon} --tol ${tol} --window ${window} --skip_wgt ${skip_wgt} --maxiter ${maxiter} --alpha ${alpha}
delay_filter_run.py ${fn} --calfile ${smooth_cal} --partial_load_Nbls ${partial_load_Nbls} --res_outfilename ${res_outfilename} --filetype_in uvh5 --filetype_out uvh5 --clobber --standoff ${standoff} --horizon ${horizon} --tol ${tol} --window ${window} --skip_wgt ${skip_wgt} --maxiter ${maxiter} --alpha ${alpha}
