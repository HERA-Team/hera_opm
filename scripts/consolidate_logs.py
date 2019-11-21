#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Script for consolidating logs from a completed makeflow run."""

from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_cleaner_ArgumentParser("logs")
args = a.parse_args()
work_dir = args.directory
output = args.output
overwrite = args.overwrite
remove_original = args.remove_original
zip_output = args.zip

print("Consolidating log files in {}".format(work_dir))
mt.consolidate_logs(work_dir, output, overwrite, remove_original, zip_output)
