#!/usr/bin/env python2.7
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration

from __future__ import print_function, division, absolute_import
import os
from hera_opm import mf_tools as mt
from hera_opm import utils

a = utils.get_makeflow_ArgumentParser()
args = a.parse_args()
obsids = args.files
config = args.config
output = args.output

obsid_list = ' '.join(obsids)
print("Generating makeflow file from config file {0} for obsids {1}".format(config, obsid_list))
mt.build_makeflow_from_config(obsids, config, output)
