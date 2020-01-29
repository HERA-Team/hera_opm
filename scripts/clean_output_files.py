#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Script for cleaning output files from a completed makeflow run."""

from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_cleaner_ArgumentParser("output")
args = a.parse_args()
work_dir = args.directory

print("Cleaning output files in {}".format(work_dir))
mt.clean_output_files(work_dir)
