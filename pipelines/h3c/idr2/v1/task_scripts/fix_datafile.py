#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
# Copyright 2020 the HERA Project
# Licensed under the MIT License

import numpy as np
from pyuvdata import UVData, utils
import argparse
import sys
import os
import shutil

# Parse arguments
a = argparse.ArgumentParser(
    description='Script for "fixing" H3C files to ensure that data is unflagged, nsamples = 1, and the uvws are correct given the antenna antenna_positions.'
)
a.add_argument("infile", help="Path to input pyuvdata-readable data file.")
a.add_argument("outfile", help="Path to output uvh5 data file.")
args = a.parse_args()

# Read data
uv = UVData()
uv.read(args.infile)

# Fix flags and nsamples
uv.flag_array = np.zeros_like(uv.flag_array)
uv.nsample_array = np.ones_like(uv.nsample_array)

# Fix uvw array using atenna postiions and array location
unique_times = np.unique(uv.time_array)
for ind, jd in enumerate(unique_times):
    inds = np.where(uv.time_array == jd)[0]
    ant_uvw = utils.phase_uvw(
        uv.telescope_location_lat_lon_alt[1],
        uv.telescope_location_lat_lon_alt[0],
        uv.antenna_positions,
    )
    ant_sort = np.argsort(uv.antenna_numbers)
    ant1_index = np.searchsorted(uv.antenna_numbers[ant_sort], uv.ant_1_array[inds])
    ant2_index = np.searchsorted(uv.antenna_numbers[ant_sort], uv.ant_2_array[inds])
    uv.uvw_array[inds] = (
        ant_uvw[ant_sort][ant2_index, :] - ant_uvw[ant_sort][ant1_index, :]
    )

# Update history
uv.history += f'\n\nData fixed to unflag all integrations, set nsamples to 1, and the correct uvw_array using the command:\n{" ".join(sys.argv)}\n\n'

# Write results to disk, deleting infile if the infile and outfiles are the same (used for when the infile is a softlink)
if args.infile == args.outfile:
    try:
        os.remove(args.infile)
    except IsADirectoryError:
        shutil.rmtree(args.infile)
uv.write_uvh5(args.outfile)
