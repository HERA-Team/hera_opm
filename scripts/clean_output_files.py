#!/usr/bin/env python2.7
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration

from __future__ import print_function, division, absolute_import
import os
from hera_op import mf_tools as mt
from hera_op import utils

a = utils.get_cleaner_ArgumentParser('output')
args = a.parse_args()
work_dir = args.directory

print("Cleaning output files in {}".format(work_dir))
mt.clean_output_files(work_dir)
