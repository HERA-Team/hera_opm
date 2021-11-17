#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Daemon script for automatically generating a makeflow for new raw data."""

import os
import time
import datetime
import subprocess

from astropy.time import Time
import redis
import h5py
import numpy as np
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from pyuvdata import UVData
import hera_mc.mc as mc
from hera_opm import mf_tools as mt

# hard-coded options
# we'll do better some day...
MONITORING_INTERVAL = 60
REDIS_HOST = "redishost"
REDIS_PORT = 6379
STORAGE_LOCATION = "/mnt/sn1"
WORKFLOW_CONFIG = (
    "/home/obs/src/hera_pipelines/pipelines/h5c/rtp/v1/h5c_rtp_stage_1.toml"
)
CONDA_ENV = "RTP"
ALLOWED_TAGS = ["engineering", "science"]

# get around potential problem of HDF5 not being able to lock files
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"

# make a redis pool and initialize connection
redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=0)
rsession = redis.Redis(connection_pool=redis_pool)

while True:
    time.sleep(MONITORING_INTERVAL)
    # check to see if the connection has gone away
    if rsession is None:
        rsession = redis.Redis(connection_pool=redis_pool)

    rkey = rsession.hget("rtp:has_new_data", "state").decode("utf-8")
    if rkey == "True":
        # fetch the list of files generated
        new_files = [
            new_file.decode("utf-8")
            for new_file in rsession.lrange("rtp:file_list", 0, -1)
        ]
        # drop diff files from list
        new_files = [new_file for new_file in new_files if "diff" not in new_file]

        file_paths = [
            os.path.join(STORAGE_LOCATION, new_file) for new_file in new_files
        ]

        # make sure we can read the metadata properly
        for filename in file_paths:
            try:
                uvd = UVData()
                uvd.read(filename, read_data=False)
            except (KeyError, OSError, ValueError):
                # ignore the file and rename it
                file_paths.remove(filename)
                new_filename = filename + ".METADATA_ERROR"
                os.rename(filename, new_filename)
                continue
            # make sure the tag is valid
            if uvd.extra_keywords["tag"] not in ALLOWED_TAGS:
                file_paths.remove(filename)

        # make sure we still have files to process
        if len(file_paths) == 0:
            # update redis
            rsession.hset("rtp:has_new_data", "state", "False")
            continue

        # make M&C RTP process events for each file
        parser = mc.get_mc_argument_parser()
        args = parser.parse_args("")
        db = mc.connect_to_mc_db(args)
        for filename in file_paths:
            try:
                # get time_array from file
                with h5py.File(filename, "r") as h5f:
                    time_array = h5f["Header/time_array"][()]
            except KeyError:
                # time_array not in file for some reason; ignore it
                file_paths.remove(filename)
                continue
            # convert time_array entry to obsid
            t0 = Time(np.unique(time_array)[0], scale="utc", format="jd")
            obsid = int(np.floor(t0.gps))

            # add to M&C
            try:
                with db.sessionmaker() as session:
                    session.add_rtp_process_event(
                        time=Time.now(), obsid=obsid, task_name="SETUP", event="queued"
                    )
            except (IntegrityError, UniqueViolation):
                continue

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
        cmd = "conda deactivate; conda activate {}; makeflow -T slurm {}\n".format(
            CONDA_ENV, mf_path
        )
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
