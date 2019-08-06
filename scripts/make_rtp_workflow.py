#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import os
import time
import datetime
from astropy.time import Time
import redis
from hera_opm import mf_tools as mt

# hard-coded options
# we'll do better some day...
MONITORING_INTERVAL = 60
REDIS_HOST = "redishost"
STORAGE_LOCATION = "/mnt/sn1"
WORKFLOW_CONFIG = "/home/obs/src/hera_opm/pipelines/h3c/rtp/v1/rtp.toml"
date = datetime.date.today().strftime("%y%m%d")
MF_LOCATION = os.path.join("/home/obs/rtp_makeflow", date)

# make a redis pool and initialize connection
redis_pool = redis.ConnectionPool(REDIS_HOST)
rsession = None

while True:
    time.sleep(MONITORING_INTERVAL)
    # check to see if the connection has gone away
    if rsession is None:
        rsession = redis.Redis(connection_pool=redis_pool)

    if rsession.hget("rtp:has_new_data", "state") == "True":
        # fetch the list of files generated
        new_files = rsession.lrange("rtp:file_list", 0, -1)
        file_paths = [
            os.path.join(STORAGE_LOCATION, new_file) for new_file in new_files
        ]

        # make target directory if it doesn't exist
        if not os.path.isdir(MF_LOCATION):
            os.makedirs(MF_LOCATION)

        # make a date stamp from the first file in the makeflow filename
        jd0 = float(new_files[0][4:17])
        t0 = Time(jd0, format="jd", out_subfmt="date_hms")
        mf_name = "rtp_{}.mf".format(t0.fits)
        mf_path = os.path.join(MF_LOCATION, mf_name)

        # make a workflow out of it
        mt.build_makeflow_from_config(file_paths, WORKFLOW_CONFIG, mf_path, MF_LOCATION)

        # update redis
        rsession.hset("rtp:has_new_data", "state", "False")
