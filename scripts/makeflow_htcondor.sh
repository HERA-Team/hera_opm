#!/bin/bash
# Copyright (c) 2019 The HERA Collaboration
# This code is licensed under the BSD 2-clause license

# This command is makeflow_htcondor.sh
# Use this to run makeflow on an HTCondor cluster environment
# Several options are set for the execution on the cluster
#
# Args:
#   1) name of makeflow file
#   2) number of simultaneous jobs to submit (optional)

# test that makeflow is on the PATH
if ! [ -x "$(command -v makeflow)"  ]; then
    echo "Error: makeflow does not seem to be installed, or is not in $PATH" >&2
    exit 1
fi

# test that file is parsable by makeflow
if [ "$#" -lt 1 ]; then
    echo "Error: please pass in the name of the makeflow as the first argument"
    exit 2
fi

if ! [ "$(makeflow_analyze -k "${1}")" ]; then
    echo "Error: makeflow file is not parsable by makeflow; please contact hera_opm maintainer"
    exit 3
fi

# actually run makeflow
# test to see if we have a second argument (number of jobs to submit simultaneously)
if [ "$#" -gt 1 ]; then
    makeflow -T condor -J "${2}" "${1}"
else
    makeflow -T condor "${1}"
fi
