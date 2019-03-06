#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file, here we define their positions,
# which must be consistent with the config.
# 1 - data filename
# 2 - calfits suffix
# 3 - path to casa executable
# 4 - casa imaging scripts dir
# 5 - spw selection
# 6 - pixel size in arcsec
# 7 - image size in Npixels
# 8 - N clean iterations
# 9 - CLEAN stopping threshold
# 10 - polarizations to image
filename="${1}"
calibration="${2}"
casa="${3}"
casa_imaging_scripts="${4}"
spw="${5}"
pxsize="${6}"
imsize="${7}"
niter="${8}"
threshold="${9}"
stokes="${10}"

# if calibration suffix is not empty, parse it and apply it
if [ ! -z "${calibration}" ]
then
    # parse calibration suffix
    cal_file="${filename%.uvh5}.${calibration}"
    echo apply_cal.py ${filename} ${filename}.calibrated --new_cal ${cal_file} --filetype_in uvh5 --filetype_out uvh5
    apply_cal.py ${filename} ${filename}.calibrated --new_cal ${cal_file} --filetype_in uvh5 --filetype_out uvh5
    filename="${filename}.calibrated"
fi

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
echo ${casa} -c ${casa_imaging_scripts}/sky_image.py --msin ${uvfits_file} --image_mfs --pxsize ${pxsize} --imsize ${imsize} --spw ${spw} --weighting briggs --robust 0 --export_fits --niter ${niter} --threshold ${threshold} --out_dir ${image_outdir} --stokes ${stokes}
${casa} -c ${casa_imaging_scripts}/sky_image.py --msin ${uvfits_file} --image_mfs --pxsize ${pxsize} --imsize ${imsize} --spw ${spw} --weighting briggs --robust 0 --export_fits --niter ${niter} --threshold ${threshold} --out_dir ${image_outdir} --stokes ${stokes}

# erase uvfits and MS file
rm ${uvfits_file}
rm -r ${image_outdir}/${ms_file}

# remove calibrated visibility
if [ ! -z "${calibration}" ]
then
    rm filename
fi
