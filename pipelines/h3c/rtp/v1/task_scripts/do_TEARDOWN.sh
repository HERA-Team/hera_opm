#!/bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# make new sessions in the librarian
librarian_assign_sessions.py local-rtp
