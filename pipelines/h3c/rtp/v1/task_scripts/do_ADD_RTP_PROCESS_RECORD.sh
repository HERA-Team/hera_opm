#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# Parameters are set in the configuration file. Here we define their positions,
# which must be consisten wtih the config.
# 1 - filename
# 2 - List of actions from config file
fn="${1}"
# This script assumes there is only one non-file argument and assigns the rest
# to actions
shift
actions="$@"
# string-ify the arguments joining with ''
# then remove "[", "]", "SETUP,", ",TEARDOWN", and ",ADD_RTP_PROCESS_RECORD"
action_string=$(join_by ''  ${actions[@]} | sed -E "s/\[|\]|(SETUP,)|(,TEARDOWN)|(,ADD_RTP_PROCESS_RECORD)//g")


echo add_rtp_process_record.py ${fn} --actions ${action_string}
add_rtp_process_record.py ${fn} --actions ${action_string}
