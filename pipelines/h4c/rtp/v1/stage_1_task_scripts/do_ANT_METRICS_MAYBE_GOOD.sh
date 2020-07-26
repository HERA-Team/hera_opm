#! /bin/bash
set -e

# This function runs atennna metrics on the antennas that, a priori, might be good (used for promoting and demoting atennnas)

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consistent with the config.
# 1 - (raw) filename
# 2 - crossCut: Modified z-score cut for most cross-polarized antenna.
# 3 - deadCut: Modified z-score cut for most likely dead antenna.
# 4 - Nbls_per_load: Number of baselines to load simultaneously.
# 5 - extension: Extension to be appended to the file name.
# 6 - maybe_good_statuses: string list of comma-separated (no spaces) antenna statuses that represent possibly "good" antennas
fn=${1}
crossCut=${2}
deadCut=${3}
Nbls_per_load=${4}
extension=${5}
maybe_good_statuses=${6}

# get exants from HERA CM database
apriori_xants=`query_ex_ants.py ${jd} ${maybe_good_statuses}`

# We only want to run ant metrics on sum files
echo ant_metrics_run.py $fn --crossCut ${crossCut} --deadCut ${deadCut} --extension ${extension} --Nbls_per_load ${Nbls_per_load} \
    --clobber --apriori_xants ${apriori_xants}
ant_metrics_run.py $fn --crossCut ${crossCut} --deadCut ${deadCut} --extension ${extension} --Nbls_per_load ${Nbls_per_load} \
    --clobber --apriori_xants ${apriori_xants}

