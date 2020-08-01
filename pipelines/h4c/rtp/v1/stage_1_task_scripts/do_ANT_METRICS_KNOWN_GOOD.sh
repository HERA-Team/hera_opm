#! /bin/bash
set -e

# This function runs atennna metrics on just the antennas known to be good apriori

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consistent with the config.
# 1 - crossCut: Modified z-score cut for most cross-polarized antenna.
# 2 - deadCut: Modified z-score cut for most likely dead antenna.
# 3 - Nbls_per_load: Number of baselines to load simultaneously.
# 4 - extension: Extension to be appended to the file name.
# 5 - known_good_statuses: string list of comma-separated (no spaces) antenna statuses that represent "good" antennas
# 6+ - filenames
crossCut=${1}
deadCut=${2}
Nbls_per_load=${3}
extension=${4}
known_good_statuses=${5}
fn1=`basename ${6}`
data_files="${@:6}"

# get exants from HERA CM database
jd=$(get_jd ${fn1})
apriori_xants=`query_ex_ants.py ${jd} ${known_good_statuses}`

# We only want to run ant metrics on sum files
echo ant_metrics_run.py ${data_files} --crossCut ${crossCut} --deadCut ${deadCut} --extension ${extension} --Nbls_per_load ${Nbls_per_load} \
    --clobber --apriori_xants ${apriori_xants}
ant_metrics_run.py ${data_files} --crossCut ${crossCut} --deadCut ${deadCut} --extension ${extension} --Nbls_per_load ${Nbls_per_load} \
    --clobber --apriori_xants ${apriori_xants}
