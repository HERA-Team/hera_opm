#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - data filename
# 2 - spw selection
# 3 - pixel size in arcsec
# 4 - image size in Npixels
filename="${1}"
spw="${2}"
pxsize="${3}"
imsize="${4}"

# convert file to uvfits
echo convert_to_uvfits.py ${filename} --overwrite
convert_to_uvfits.py ${filename} --overwrite

# call sky_image.py from CASA_IMAGING package
echo /home/casa/packages/RHEL7/release/casa-release-5.1.0-68/bin/casa -c sky_image.py --msin ${filename} --image_mfs --pxsize ${pxsize} --imsize ${imsize} --spw ${spw} --weighting briggs --robust 0 --export_fits
/home/casa/packages/RHEL7/release/casa-release-5.1.0-68/bin/casa -c sky_image.py --msin ${filename} --image_mfs --pxsize ${pxsize} --imsize ${imsize} --spw ${spw} --weighting briggs --robust 0 --export_fits

# erase uvfits and MS file


