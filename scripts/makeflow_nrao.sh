#!/bin/bash
# Copyright (c) 2018 The HERA Collaboration
# This code is licensed under the BSD 2-clause license

# This command is makeflow_nrao.sh
# Use this to run makeflow on the NRAO cluster environment
# Several options are set for the execution on the cluster

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

if ! [ "$(makeflow_analyze -k $1)" ]; then
    echo "Error: makeflow file is not parsable by makeflow; please contact hera_opm maintainer"
    exit 3
fi

# make sure that we're on the right host
if [ "$(hostname)" != "herapost-master" ]; then
    echo "Error: batch submission jobs can only be run from herapost-master; please log in there and retry"
    exit 4
fi

# actually run makeflow
# use cluster processing options
makeflow -T torque $1
