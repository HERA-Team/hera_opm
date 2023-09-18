#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Script for generating a makeflow from a config and list of files."""

import sys
import os
from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_makeflow_ArgumentParser()
args = a.parse_args()
obsids = args.files
config = args.config
output = args.output
scan_files = args.scan_files
rename_bad_files = args.rename_bad_files
bad_suffix = args.bad_suffix
work_dir = args.work_dir

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
            if rename_bad_files:
                os.rename(obsid, obsid + bad_suffix)

obsid_list = " ".join(obsids)
print(f"Generating makeflow file from config file {config} for obsids {obsid_list}")
mt.build_makeflow_from_config(obsids, config, output, work_dir=work_dir)

for obsid in bad_metadata_obsids:
    print(f"Bad metadata in {obsid}")
    if rename_bad_files:
        print(f"    Moved to {obsid + bad_suffix}")
