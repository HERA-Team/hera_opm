#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2020 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Script for fixing some issues with H3C data files and possibly renaming."""

import numpy as np
from pyuvdata import UVData
import argparse

ap = argparse.ArgumentParser()
ap.prog = "fix_h3c_data_file.py"
ap.add_argument(
    "filenames",
    metavar="filenames",
    nargs="*",
    type=str,
    default=[],
    help="File to correct flag_array and nsample_array.",
)
args = ap.parse_args()

uv = UVData()

for filename in args.filenames:
    uv.read(filename)
    uv.flag_array = np.zeros_like(uv.flag_array)
    uv.nsample_array = np.ones_like(uv.nsample_array)
    uv.history += (
        "Corrected flag_array and nsmaple_array with hera_opm/fix_h3c_data_file.py"
    )
    uv.write_uvh5(filename, clobber=True)
