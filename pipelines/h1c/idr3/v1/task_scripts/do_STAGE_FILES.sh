#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# unpack positional arguments
fn="${1}"

# stage the files to lustre from the librarian
# we need to get all 4 files from the librarian, but we can use wildcards to match
target_fn=$(replace_pol $fn '%')
json_search="\{\"name-matches\": \"${target_fn}\"\}"
# wait until the staging is done to return
echo librarian_stage_files.py -w local . $json_search
librarian_stage_files.py -w local . $json_search
