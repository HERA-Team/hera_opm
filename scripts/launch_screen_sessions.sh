#!/bin/bash
# Copyright 2019 The HERA Collaboration
# This code is licensed under the BSD 2-clause License

# This script is launch_screen_sessions.sh.
# Use this script to create screen sessions, automatically create
# a makeflow from a TOML file, and run the makeflow.
#
# Args:
#   1) path to the .toml file
#   2) path to folder with data files
#   3) ending of data files. Files will be enumerated
#      by using a glob `*.ending'
#   4) number of simultaneous batch jobs to run, optional
#
# Example usage:
#   launch_screen_sessions.sh idr2_2.toml /lustre/aoc/projects/hera/H1C_IDR2/IDR2_2 .HH.uvh5 20
#
# In the sample above, the folder IDR2_2 contains a series of folders
# indexed by JD (e.g., 2458098, 2458099, etc.). These folders contain
# the raw data files used by hera_opm to generate a workflow, with the
# extension given by the third argument (.HH.uvh5). The optional fourth
# argument gives the number of simiultaneous jobs to submit **for each day
# in the workflow**.

# get full path of toml file, in case it's not absolute
toml_path=`realpath "${1}"`

# get current environment, to activate inside of screen
# should be an environment with hera_opm installed, because
# `makeflow_nrao.sh' is called inside
conda_env=`conda info --envs | grep '*' | cut -d ' ' -f1`

# make list of JDs to process
# defaults to all JD-like folders contained in argument $2
JD_LIST=`ls "${2}" | egrep "[0-9]{7}" | tr '\n' ' '`

# loop over days
for JD in ${JD_LIST}; do
    # make encapsulating folder
    mkdir -p "${JD}"

    # build makeflow
    cd "${JD}"
    file_list=`ls "${2}"/"${JD}"/*"${3}" | tr '\n' ' '`
    build_makeflow_from_config.py -c "${toml_path}" ${file_list}

    # get full path to .mf file
    mf_file=`realpath *.mf`

    # build command to be fed to screen session
    if [ "$#" -gt 3 ]; then
    	cmd="conda activate $conda_env; makeflow_nrao.sh ${mf_file} ${4}\n"
    else
    	cmd="conda activate $conda_env; makeflow_nrao.sh ${mf_file}\n"
    fi

    # launch screen session named by JD and send commands
    screen -d -m -S "${JD}"
    screen -S "${JD}" -p 0 -X stuff "${cmd}"

    # go back up a level
    cd ..
done
