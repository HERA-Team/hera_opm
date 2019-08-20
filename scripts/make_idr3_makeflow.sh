#!/bin/bash
# This is make_idr3_makeflow.sh
# Stage raw data files for a given day at NRAO, then
# build a makeflow for that day.
#
# Positional arguments:
# 1 - JD
# 2 - directory to stage files
# 3 - config file to use for makeflow
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
config_file="${3}"

# The JSON search string doesn't need to be wrapped in single-quotes
# if passed as an argument rather than entered interactively.
json_string='{"name-matches": "zen.'"$jd"'.%.uv"}'
librarian_stage_files.py -w local $stagedir "$json_string"

# Also grab the ant_metrics files
json_string='{"name-matches": "zen.'"$jd"'.%.ant_metrics.json"}'
librarian_stage_files.py -w local $stagedir "$json_string"

# Now make a makeflow
input_files=`ls -d1 $stagedir/$jd/zen.*.xx.HH.uv | tr '\n' ' '`
build_makeflow_from_config.py -c $config_file $input_files
