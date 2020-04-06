#! /bin/bash
set -e

# This function sets all the flags to False and all the nsamples to 1 and overwrites the file

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - filename

fn="${1}"

echo python -c "import numpy as np; \
                from pyuvdata import UVData; \
                uv = UVData(); \
                uv.read('"${fn}"'); \
                uv.flag_array = np.zeros_like(uv.flag_array); \
                uv.nsample_array = np.ones_like(uv.nsample_array); \
                uv.write_uvh5('"${fn}"', clobber=True)"
python -c "import numpy as np; \
           from pyuvdata import UVData; \
           uv = UVData(); \
           uv.read('"${fn}"'); \
           uv.flag_array = np.zeros_like(uv.flag_array); \
           uv.nsample_array = np.ones_like(uv.nsample_array); \
           uv.write_uvh5('"${fn}"', clobber=True)"
