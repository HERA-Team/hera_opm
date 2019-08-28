#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# refresh the IERS table for calculating LST accurately
python -c "from astropy.utils.data import clear_download_cache; clear_download_cache()"
python -c "from astropy.time import Time; t = Time.now(); t.ut1"
