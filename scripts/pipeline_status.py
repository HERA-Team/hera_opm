#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD Licnse
"""Script for checking the status of a HERA makeflow pipeline."""

import numpy as np
import glob
from hera_opm.mf_tools import get_config_entry
import toml
import os
from dateutil import parser as dateparser
import argparse

# Parse arguments
parser = argparse.ArgumentParser(
    description="Check the status of a pipeline. Prints out the total number of jobs of each "
    "task in the workflow (by the wrapper*.sh files), the number completed (by the .out "
    "files), the number currently running (which have starting but not stopping times in the"
    ".log files), and the number errored (which have stopping times in the log but no .out"
    "file). Also prints the average time elapsed for non-trivial jobs (i.e. those that take"
    "more than a second)."
)
parser.add_argument(
    "--config_file",
    type=str,
    required=True,
    help="Absolute path to makeflow .cfg file.",
)
parser.add_argument(
    "--working_dir",
    nargs="*",
    type=str,
    required=True,
    help="Absolute path to pipeline working directory (or directories using *).",
)
args = parser.parse_args()
if np.all([not os.path.isdir(wdir) for wdir in args.working_dir]):
    raise ValueError("You must supply at least one directory using --working_dir")

# Read makeflow config file
config = toml.load(args.config_file)
workflow = get_config_entry(config, "WorkFlow", "actions")
try:
    timeout = get_config_entry(config, "Options", "timeout")
    timeout = (
        float(
            eval(
                timeout.replace("s", "")
                .replace("m", "*60")
                .replace("h", "*60*60")
                .replace("d", "*60*60*24")
            )
        )
        / 60.0
    )
except BaseException:
    timeout = None


def elapsed_time(log_lines):
    """Take a list of lines in a log file and calculates the elapsed time in minutes.

    Parameters
    ----------
    log_lines : list of str
        List of lines in a log file, like that produced by [file].readlines().

    Returns
    -------
    runtime : float or int
        The runtime in minutes. If the file has a start time but no end time,
        returns -1. If the file has no start time, returns -2.
    """
    try:
        start = dateparser.parse(log_lines[0], ignoretz=True)
    except BaseException:
        start = None
    try:
        end = dateparser.parse(log_lines[-1], ignoretz=True)
    except BaseException:
        end = None

    if (start is not None) and (end is None):
        return -1  # currently running
    elif start is None:
        return -2  # never started
    else:
        return ((end - start).seconds + 24.0 * 60 * 60 * (end - start).days) / 60.0


def inspect_log_files(log_files, out_files):
    """Look at log files, compute the average non-zero runtime, and print example errors.

    Parameters
    ----------
    log_files : list of str
        A list of the .log files.
    out_files : list of str
        A list of the .out files.

    Returns
    -------
    average_runtime : float
        The average runtime of all finished jobs that took longer than a second, in minutes.
    nRunning : int
        The number of jobs believed to be running (start time with no stop time).
    nErrored : int
        The number of jobs believed to have been terminated for errors ().
    nTimedOut : int
        The number of jobs that terminated within 1% of the wall-time specified for timeouts.

    """
    error_warned = False
    runtimes = []
    errored_logs = []
    timed_out_logs = []
    for log_file in log_files:
        with open(log_file, "r") as f:
            log_lines = f.readlines()
        runtimes.append(elapsed_time(log_lines))

        # It timed out
        if (
            timeout is not None
            and (np.abs(runtimes[-1]) > 0.99 * timeout)
            and (log_file.replace(".log", ".out") not in out_files)
            and (log_file.replace(".log.error", ".out") not in out_files)
        ):
            timed_out_logs.append(log_file)
        # It ran but there's no .out, so it errored
        elif ".log.error" in log_file:
            errored_logs.append(log_file)
            if error_warned:
                print("Errors also suspected in", log_file)
            else:
                print("\n\nError Suspected (no .out found) in", log_file)
                print("------------------------------------------------\n")
                print("".join(log_lines))
                print("------------------------------------------------\n")
                error_warned = True
    if error_warned:
        print("\n")
    if len(timed_out_logs) > 0:
        print("\nTimeouts (wall-time > " + str(timeout) + " minutes) detected in:")
        for log in timed_out_logs:
            print(log)
        print("\n")

    runtimes = np.array(runtimes)
    finished_runtimes = runtimes[runtimes > 10.0 / 60.0]
    if len(finished_runtimes) > 0:
        average_runtime = np.mean(finished_runtimes)
    else:
        average_runtime = np.nan

    return (
        average_runtime,
        np.sum(runtimes == -1),
        len(errored_logs),
        len(timed_out_logs),
    )


def filter_errors(log_files):
    """Choose the newer of the log or error files.

    Parameters
    ----------
    log_files : list of str
        The list of log files to check.

    Returns
    -------
    newest_log_files : list of str
        The list of files containing the newest entry for each file.

    """
    newest_log_files = []
    unique_bases = np.unique([f.replace(".log.error", ".log") for f in log_files])
    for log_file in unique_bases:
        err_file = log_file.replace(".log", ".log.error")
        if (
            err_file in log_files and log_file in log_files
        ):  # both an error file and a log file
            with open(err_file, "r") as f:
                err_lines = f.readlines()
                err_start = dateparser.parse(err_lines[0], ignoretz=True)
            with open(log_file, "r") as f:
                log_lines = f.readlines()
                log_start = dateparser.parse(log_lines[0], ignoretz=True)
            if err_start < log_start:
                newest_log_files.append(log_file)
            else:
                newest_log_files.append(err_file)
        elif err_file in log_files:  # just an error file
            newest_log_files.append(err_file)
        else:  # just a log file
            newest_log_files.append(log_file)
    return newest_log_files


# Run pipeline report
print("---------------\nPIPELINE REPORT\n---------------\n")
for job in workflow:
    print(job + ":")
    total, logged, done = [], [], []
    for wdir in args.working_dir:
        if os.path.isdir(wdir):
            total += glob.glob(os.path.join(wdir, "wrapper_*." + job + ".*sh"))
            logged += glob.glob(os.path.join(wdir, "*." + job + ".*log*"))
            done += glob.glob(os.path.join(wdir, "*." + job + ".*out"))
    logged = filter_errors(logged)
    average_runtime, nRunning, nErrored, nTimedOut = inspect_log_files(logged, done)

    print("Average (non-trivial) runtime:", average_runtime, "minutes")
    print(
        len(total),
        "\t|\t",
        len(done),
        "\t|\t",
        nRunning,
        "\t|\t",
        nErrored,
        "\t|\t",
        nTimedOut,
    )
    print("total\t|\tdone\t|\trunning\t|\terrored\t|\ttimed out\n\n")
