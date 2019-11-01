#!/bin/bash
# This is make_idr3_makeflow.sh
# Stage raw data files for a given day at NRAO, then
# build a makeflow for that day.
#
# Positional arguments:
# 1 - JD
# 2 - directory to stage files
# 3 - directory to put makeflow working files and logs
# 4 - config file to use for makeflow
# 5 - conda environment to activate for staging and running pipeline
# 6 - number of concurrent tasks to run as part of makeflow process
#
# Note: due to how the librarian stages files, the files
# will be created underneath the specified directory in a
# directory whose name is the JD. For instance, if the
# script is invoked as:
#   stage_jd.sh 2458088 /path/to/staging/dir idr3_1.toml
# the files will be placed in:
#   /path/to/staging/dir/2458088/<file_names.uv>

jd="${1}"
stagedir="${2}"
workdir="${3}"
config_file="${4}"
conda_env="${5}"
ntasks="${6}"

# activate conda env
source ~/.bashrc
conda activate $conda_env

# get current directory
current_dir=`pwd`

# move to workdir
cd $workdir

# The JSON search string doesn't need to be wrapped in single-quotes
# if passed as an argument rather than entered interactively.
json_string='{"name-matches": "zen.'"$jd"'.%.uv"}'
librarian stage-files -w local $stagedir "$json_string"

# Also grab the ant_metrics files
json_string='{"name-matches": "zen.'"$jd"'.%.ant_metrics.json"}'
librarian stage-files -w local $stagedir "$json_string"

# Now make a makeflow
input_files=`ls -d1 $stagedir/$jd/zen.*.xx.HH.uv | tr '\n' ' '`
build_makeflow_from_config.py -c $config_file $input_files

mf_file=`realpath *.mf`

# build command to be fed to screen session
if [ "$#" -gt 5 ]; then
    cmd="conda activate $conda_env; makeflow_nrao.sh ${mf_file} ${ntasks}; if [ $? -eq 0 ]; then touch succeeded.out; else touch failed.out; fi; exit\n"
else
    cmd="conda activate $conda_env; makeflow_nrao.sh ${mf_file}; if [ $? -eq 0 ]; then touch succeeded.out; else touch failed.out; fi; exit\n"
fi

# launch screen session named by JD and send commands
screen -d -m -S "${jd}"
screen -S "${jd}" -p 0 -X stuff "${cmd}"

# go back to main directory
cd $current_dir
