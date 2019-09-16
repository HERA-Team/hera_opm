#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Daemon script for automatically generating a makeflow for new raw data."""

from __future__ import print_function, division, absolute_import

import os
import sys
import time
import datetime
import subprocess

from astropy.time import Time
import redis

from hera_opm import mf_tools as mt

# hard-coded options
# we'll do better some day...
MONITORING_INTERVAL = 60
REDIS_HOST = "redishost"
REDIS_PORT = 6379
STORAGE_LOCATION = "/mnt/sn1"
WORKFLOW_CONFIG = "/home/obs/src/hera_opm/pipelines/h3c/rtp/v1/rtp.toml"
CONDA_ENV = "RTP"

# make a redis pool and initialize connection
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
rsession = redis.Redis(connection_pool=redis_pool)

while True:
    time.sleep(MONITORING_INTERVAL)
    # check to see if the connection has gone away
    if rsession is None:
        rsession = redis.Redis(connection_pool=redis_pool)

    rkey = rsession.hget("rtp:has_new_data", "state")
    if sys.version_info.major > 2:
        rkey = rkey.decode("utf-8")
    if rkey == "True":
        # fetch the list of files generated
        new_files = rsession.lrange("rtp:file_list", 0, -1)
        if sys.version_info.major > 2:
            new_files = [new_file.decode("utf-8") for new_file in new_files]
        file_paths = [
            os.path.join(STORAGE_LOCATION, new_file) for new_file in new_files
        ]

        # make target directory if it doesn't exist
        date = datetime.date.today().strftime("%y%m%d")
        MF_LOCATION = os.path.join("/home/obs/rtp_makeflow", date)
        if not os.path.isdir(MF_LOCATION):
            os.makedirs(MF_LOCATION)

        # make a date stamp from the first file in the makeflow filename
        jd0 = float(new_files[0][4:17])
        t0 = Time(jd0, format="jd", out_subfmt="date_hms")
        mf_name = "rtp_{}.mf".format(t0.isot)
        mf_path = os.path.join(MF_LOCATION, mf_name)

        # change working location
        os.chdir(MF_LOCATION)

        # make a workflow
        mt.build_makeflow_from_config(file_paths, WORKFLOW_CONFIG, mf_path, MF_LOCATION)

        # launch workflow inside of screen
        cmd = "conda activate {}; makeflow -T slurm {}\n".format(CONDA_ENV, mf_path)
        screen_name = "rtp_{}".format(str(int(jd0)))
        screen_cmd1 = ["screen", "-d", "-m", "-S", screen_name]
        screen_cmd2 = ["screen", "-S", screen_name, "-p", "0", "-X", "stuff", cmd]
        try:
            subprocess.check_call(screen_cmd1)
            subprocess.check_call(screen_cmd2)
        except subprocess.CalledProcessError as e:
            raise ValueError(
                "Error spawning screen session; command was {}; returncode was {:d}; "
                "output was {}; stderr was {}".format(
                    e.cmd, e.returncode, e.output, e.stderr
                )
            )

        # update redis
        rsession.hset("rtp:has_new_data", "state", "False")
