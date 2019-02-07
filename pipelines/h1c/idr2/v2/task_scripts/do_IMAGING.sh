#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - data filename
# 2 - path to casa executable
# 3 - casa imaging scripts dir
# 4 - spw selection
# 5 - pixel size in arcsec
# 6 - image size in Npixels
# 7 - N clean iterations
# 8 - CLEAN stopping threshold
filename="${1}"
casa="${2}"
casa_imaging_scripts="${3}"
spw="${4}"
pxsize="${5}"
imsize="${6}"
niter="${7}"
threshold="${8}"

# convert file to uvfits
echo convert_to_uvfits.py ${filename} --overwrite
convert_to_uvfits.py ${filename} --overwrite

# get uvfits and ms filename
uvfits_file="${filename%.uvh5}.uvfits"
ms_file="${filename%.uvh5}.ms"

# make an imaging dir for outputs
image_outdir="${filename}_image"
mkdir $image_outdir

# call sky_image.py from CASA_IMAGING package
echo ${casa} -c ${casa_imaging_scripts}/sky_image.py --msin ${uvfits_file} --image_mfs --pxsize ${pxsize} --imsize ${imsize} --spw ${spw} --weighting briggs --robust 0 --export_fits --niter ${niter} --threshold ${threshold} --out_dir ${image_outdir}
${casa} -c ${casa_imaging_scripts}/sky_image.py --msin ${uvfits_file} --image_mfs --pxsize ${pxsize} --imsize ${imsize} --spw ${spw} --weighting briggs --robust 0 --export_fits --niter ${niter} --threshold ${threshold} --out_dir ${image_outdir}

# erase uvfits and MS file
rm ${uvfits_file}
rm -r ${image_outdir}/${ms_file}
