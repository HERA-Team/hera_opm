#!/bin/bash
set -e

#arg #2 is "prev_basename"
# if there _isn't_ a previous basename then we probably have the first
if [ $2 == "None" ];
then
    # import common functions
    src_dir="$(dirname "$0")"
    source ${src_dir}/_common.sh

    # make new sessions in the librarian
    librarian assign-sessions local-rtp
fi
