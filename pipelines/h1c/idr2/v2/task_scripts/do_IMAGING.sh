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
# 4 - calfits suffix (optional)
filename="${1}"
casa="${2}"
casa_imaging_scripts="${3}"
if [ "$#" -ge 4 ]; then
    calibration="${4}"
fi

# if calibration suffix is not empty, parse it and apply it
if [ ! -z "${calibration}" ]; then
    # parse calibration suffix
    cal_file="${filename%.uvh5}.${calibration}"
    echo apply_cal.py ${filename} ${filename%.uvh5}.calibrated.uvh5 --new_cal ${cal_file} --filetype_in uvh5 --filetype_out uvh5 --clobber
    apply_cal.py ${filename} ${filename%.uvh5}.calibrated.uvh5 --new_cal ${cal_file} --filetype_in uvh5 --filetype_out uvh5 --clobber
    filename="${filename%.uvh5}.calibrated.uvh5"
fi

# convert file to uvfits
echo convert_to_uvfits.py ${filename} --output_filename ${filename%.uvh5}.uvfits --overwrite
convert_to_uvfits.py ${filename} --output_filename ${filename%.uvh5}.uvfits --overwrite

# get uvfits and ms filename
uvfits_file="${filename%.uvh5}.uvfits"
uvfits_file_out="${filename}.image"
ms_file="${filename%.uvh5}.ms"

# get current directory
cwd=`pwd`

# make an imaging dir for outputs
image_outdir="${filename}_image"
mkdir -p ${image_outdir}
cd ${image_outdir}

# call sky_image.py from CASA_IMAGING package
echo ${casa} -c ${casa_imaging_scripts}/opm_imaging.py --uvfitsname ${cwd}/${uvfits_file} --image ${uvfits_file_out}
${casa} -c ${casa_imaging_scripts}/opm_imaging.py --uvfitsname ${cwd}/${uvfits_file} --image ${uvfits_file_out}

# erase uvfits file
cd ${cwd}
echo rm ${uvfits_file}
rm ${uvfits_file}

# keep ms files for 2458098
JD=`get_jd "${1}" | cut -c 1-7`
if [ $JD -ne 2458098 ]; then
    echo rm ${ms_file}
    rm -r ${ms_file} || echo "No ${ms_file} to remove."
fi

# remove calibrated visibility
if [ ! -z "${calibration}" ]; then
    rm ${filename}
fi
