#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Script for generating a makeflow from a config and list of files."""

import sys
from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_makeflow_ArgumentParser()
args = a.parse_args()
obsids = args.files
config = args.config
output = args.output
scan_files = args.scan_files

bad_metadata_obsids = []
if scan_files:
    try:
        from pyuvdata import UVData
    except ImportError:
        sys.exit("pyuvdata must be installed to use --scan-files option")
    for obsid in obsids:
        try:
            uvd = UVData()
            uvd.read(obsid, read_data=False)
        except (KeyError, OSError, ValueError):
            bad_metadata_obsids.append(obsid)
            obsids.remove(obsid)

obsid_list = " ".join(obsids)
print(
    "Generating makeflow file from config file {0} for obsids {1}".format(
        config, obsid_list
    )
)
mt.build_makeflow_from_config(obsids, config, output)

for obsid in bad_metadata_obsids:
    print(f"Bad metadata in {obsid}")
