#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Script for cleaning wrapper scripts from a completed makeflow run."""

from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_cleaner_ArgumentParser("wrapper")
args = a.parse_args()
work_dir = args.directory

print("Cleaning wrapper scripts in {}".format(work_dir))
mt.clean_wrapper_scripts(work_dir)
