#!/bin/bash
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License

# This command is makeflow_local.sh
# Use this to run makeflow on a local machine (i.e., on a laptop, or interactively on a cluster node)
# This is a thin wrapper around makeflow, with some checking for consistency built in

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

# actually run makeflow
makeflow $1
