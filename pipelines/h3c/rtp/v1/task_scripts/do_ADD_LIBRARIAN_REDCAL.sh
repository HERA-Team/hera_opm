#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consistent wtih the config.
# 1 - (raw) filename
# 2 - iter0_prefix: if not "", save omnical results after the 0th interation with this prefix iff there will be a rerun
fn=${1}
iter0_prefix=${2}

# get the integer portion of the JD
jd=$(get_int_jd ${1})


# We only want to upload ant metrics on sum files
# check if the string does not contain the word diff
if ! stringContain diff "${fn}"; then

  # Upload firstcal results
  firstcal_f = `echo ${fn%.uvh5}.first.calfits`
  echo librarian upload local-rtp ${firstcal_f} ${jd}/${firstcal_f}
  librarian upload local-rtp ${firstcal_f} ${jd}/${firstcal_f}

  # Upload omnical results
  omnical_f = `echo ${fn%.uvh5}.omni.calfits`
  echo librarian upload local-rtp ${omnical_f} ${jd}/${omnical_f}
  librarian upload local-rtp ${omnical_f} ${jd}/${omnical_f}

  # Upload omnical visibility solutions
  omnivis_f = `echo ${fn%.uvh5}.omni_vis.uvh5`
  echo librarian upload local-rtp ${omnivis_f} ${jd}/${omnivis_f}
  librarian upload local-rtp ${omnivis_f} ${jd}/${omnivis_f}

  # Upload omnical visibility solutions
  omnimeta_f = `echo ${fn%.uvh5}.omni_meta.hdf5`
  echo librarian upload local-rtp ${omnimeta_f} ${jd}/${omnimeta_f}
  librarian upload local-rtp ${omnimeta_f} ${jd}/${omnimeta_f}

  # check if iter0 is not empty
  if [ ! -z "$iter0_prefix" ]; then
    iter0_firstcal_f=`echo ${fn%.uvh5}${iter0_prefix}.first.calfits`
    # check if iter0_firstcal_f exists (not guaranteed if no re-run is triggered)
    if [ -f "$iter0_firstcal_f" ]; then
        echo librarian upload local-rtp ${iter0_firstcal_f} ${jd}/${iter0_firstcal_f}
        librarian upload local-rtp ${iter0_firstcal_f} ${jd}/${iter0_firstcal_f}
    fi

    iter0_omnical_f=`echo ${fn%.uvh5}${iter0_prefix}.omni.calfits`
    # check if iter0_omnical_f exists (not guaranteed if no re-run is triggered)
    if [ -f "$iter0_omnical_f" ]; then
        echo librarian upload local-rtp ${iter0_omnical_f} ${jd}/${iter0_omnical_f}
        librarian upload local-rtp ${iter0_omnical_f} ${jd}/${iter0_omnical_f}
    fi

    iter0_omnivis_f=`echo ${fn%.uvh5}${iter0_prefix}.omni_vis.uvh5`
    # check if iter0_omnivis_f exists (not guaranteed if no re-run is triggered)
    if [ -f "$iter0_omnivis_f" ]; then
        echo librarian upload local-rtp ${iter0_omnivis_f} ${jd}/${iter0_omnivis_f}
        librarian upload local-rtp ${iter0_omnivis_f} ${jd}/${iter0_omnivis_f}
    fi

    iter0_omnimeta_f=`echo ${fn%.uvh5}${iter0_prefix}.omni_meta.hdf5`
    # check if iter0_omnimeta_f exists (not guaranteed if no re-run is triggered)
    if [ -f "$iter0_omnivis_f" ]; then
        echo librarian upload local-rtp ${iter0_omnimeta_f} ${jd}/${iter0_omnimeta_f}
        librarian upload local-rtp ${iter0_omnimeta_f} ${jd}/${iter0_omnimeta_f}
    fi
  fi
fi
