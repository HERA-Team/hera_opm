#!/usr/bin/env python2.7
# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration

from __future__ import print_function, division, absolute_import
import os
from hera_op import mf_tools as mt
from hera_op import utils

a = utils.get_makeflow_ArgumentParser()
args = a.parse_args()
obsids = args.obsids
config = args.config_file
output = args.mf_file

obsid_list = ' '.join(obsids)
print("Generating {0} makeflow file from config file {1} for obsids {2}".format(output, config, obsid_list))
mt.build_makeflow_from_config(obsids, config, output)
