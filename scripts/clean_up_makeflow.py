#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Clean up after a makeflow has completed."""

from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_cleaner_ArgumentParser("logs")
# change program name to reflect script
a.prog = "clean_up_makeflow.py"
args = a.parse_args()
work_dir = args.directory

# call wrapper cleaner function
print("Cleaning wrapper scripts in {}".format(work_dir))
mt.clean_wrapper_scripts(work_dir)

# call output cleaner function
print("Cleaning output files in {}".format(work_dir))
mt.clean_output_files(work_dir)

# call log-making function
output = args.output
overwrite = args.overwrite
remove_original = args.remove_original
zip_output = args.zip

print("Consolidating log files in {}".format(work_dir))
mt.consolidate_logs(work_dir, output, overwrite, remove_original, zip_output)
