#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD Licnse
"""Script for checking the status of a HERA makeflow pipeline."""

import numpy as np
import fnmatch
import re
from hera_opm.mf_tools import get_config_entry
import toml
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from dateutil import parser as dateparser
import argparse

# Number of threads used to read log files. Reads on networked filesystems (e.g. Lustre)
# are latency-bound, so reading many files at once is much faster than one at a time.
N_READ_THREADS = 16

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

# Matches the output of `date` in the wrapper scripts, e.g. "Wed Nov 29 15:25:30 MST 2017"
# or "Wed Nov  5 03:25:30 PM MST 2017"
DATE_REGEX = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) +"
    r"(\d{1,2}) (\d{2}):(\d{2}):(\d{2})(?: (AM|PM))? ([A-Z]{3,5}) (\d{4})"
)
MONTHS = {
    month: i + 1
    for i, month in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())
}


@lru_cache(maxsize=None)
def _dateutil_ignores_tz(tz):
    """Check that dateutil treats `tz` as a time zone name, which ignoretz=True drops."""
    try:
        parsed = dateparser.parse(f"Mon Jan  1 00:00:00 {tz} 2001", ignoretz=True)
    except BaseException:
        return False
    return parsed == datetime(2001, 1, 1)


def parse_date(line):
    """Parse a timestamp the way dateutil would (ignoring time zones), but faster.

    dateutil's parser is slow, so lines in the format written by `date` are parsed
    directly. Anything else falls back to dateutil.

    Parameters
    ----------
    line : str
        The line of text to parse.

    Returns
    -------
    date : datetime.datetime or None
        The (time zone naive) parsed date, or None if the line could not be parsed.
    """
    match = DATE_REGEX.fullmatch(line.strip())
    if match is not None and _dateutil_ignores_tz(match[7]):
        month, day, hour, minute, second, ampm, _, year = match.groups()
        hour = int(hour)
        # dateutil rejects 12-hour clock times with hours > 12, so let it handle those
        if ampm is None or hour <= 12:
            if ampm == "PM" and hour < 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0
            try:
                return datetime(
                    int(year), MONTHS[month], int(day), hour, int(minute), int(second)
                )
            except ValueError:
                pass  # e.g. an invalid day of the month; let dateutil handle it
    try:
        return dateparser.parse(line, ignoretz=True)
    except BaseException:
        return None


def elapsed_time(first_line, last_line):
    """Take the first and last lines of a log file and calculates the elapsed time in minutes.

    Parameters
    ----------
    first_line : str
        The first line of a log file, like that produced by [file].readlines().
    last_line : str
        The last line of a log file, like that produced by [file].readlines().

    Returns
    -------
    runtime : float or int
        The runtime in minutes. If the file has a start time but no end time,
        returns -1. If the file has no start time, returns -2.
    """
    start = parse_date(first_line)
    end = parse_date(last_line)

    if (start is not None) and (end is None):
        return -1  # currently running
    elif start is None:
        return -2  # never started
    else:
        return ((end - start).seconds + 24.0 * 60 * 60 * (end - start).days) / 60.0


def read_first_and_last_lines(log_file):
    """Read the first and last lines of a file without reading the whole file.

    Parameters
    ----------
    log_file : str
        The file to read.

    Returns
    -------
    first_line : str
        The first line of the file ("" if the file is empty).
    last_line : str
        The last line of the file ("" if the file is empty).
    """
    with open(log_file, "rb") as f:
        first_line = f.readline().decode(errors="ignore")
        try:
            # Seek to the end and back up a bit to catch the last line
            f.seek(-64, os.SEEK_END)
        except OSError:
            # If that fails, read the whole file
            f.seek(0)
        lines = f.readlines()
    last_line = lines[-1].decode(errors="ignore") if len(lines) > 0 else ""
    return first_line, last_line


def inspect_log_files(log_files, out_files, log_lines):
    """Look at log files, compute the average non-zero runtime, and print example errors.

    Parameters
    ----------
    log_files : list of str
        A list of the .log files.
    out_files : set of str
        A set of the .out files.
    log_lines : dict
        Maps each .log file to a tuple of its first and last lines.

    Returns
    -------
    average_runtime : float
        The average runtime of all finished jobs that took longer than 10 seconds, in minutes.
    total_runtime : float
        The total runtime of all finished jobs, in hours.
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
        runtimes.append(elapsed_time(*log_lines[log_file]))

        # Check if this .log file is missing the corresponding .out file
        if (log_file.replace(".log", ".out") not in out_files) and (
            log_file.replace(".log.error", ".out") not in out_files
        ):
            # It timed out
            if timeout is not None and (np.abs(runtimes[-1]) > 0.99 * timeout):
                timed_out_logs.append(log_file)
            # It ran but there's no .out, so it errored
            elif ".log.error" in log_file:
                errored_logs.append(log_file)
                if error_warned:
                    print("Errors also suspected in", log_file)
                else:
                    with open(log_file, "r") as f:
                        log_lines_full = f.readlines()
                    print("\n\nError Suspected (no .out found) in", log_file)
                    print("------------------------------------------------\n")
                    print("".join(log_lines_full))
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
        np.sum(runtimes[runtimes > 0]) / 60.0,
        np.sum(runtimes == -1),
        len(errored_logs),
        len(timed_out_logs),
    )


def filter_errors(log_files, log_lines):
    """Choose the newer of the log or error files.

    Parameters
    ----------
    log_files : list of str
        The list of log files to check.
    log_lines : dict
        Maps each log file to a tuple of its first and last lines.

    Returns
    -------
    newest_log_files : list of str
        The list of files containing the newest entry for each file.

    """
    log_files = set(log_files)
    newest_log_files = []
    unique_bases = sorted({f.replace(".log.error", ".log") for f in log_files})
    for log_file in unique_bases:
        err_file = log_file.replace(".log", ".log.error")
        if (
            err_file in log_files and log_file in log_files
        ):  # both an error file and a log file
            err_start = parse_date(log_lines[err_file][0])
            log_start = parse_date(log_lines[log_file][0])
            # if the .log has no start time yet, it's a retry that just started
            if err_start is None or log_start is None or err_start < log_start:
                newest_log_files.append(log_file)
            else:
                newest_log_files.append(err_file)
        elif err_file in log_files:  # just an error file
            newest_log_files.append(err_file)
        else:  # just a log file
            newest_log_files.append(log_file)
    return newest_log_files


# List each working directory just once, rather than globbing it several times per job,
# since listing large directories is slow on networked filesystems (e.g. Lustre)
dir_listings = [
    (wdir, os.listdir(wdir)) for wdir in args.working_dir if os.path.isdir(wdir)
]


def find_files(pattern, job):
    """Find the files in the working directories matching a glob pattern for a job.

    Parameters
    ----------
    pattern : str
        The glob pattern to match, which must contain "." + job + ".".
    job : str
        The name of the job.

    Returns
    -------
    files : list of str
        The paths to the matching files, like those returned by glob.glob.
    """
    regex = re.compile(fnmatch.translate(pattern))
    # check for this substring first, since it's much faster than the regex
    job_str = "." + job + "."
    return [
        os.path.join(wdir, name)
        for wdir, names in dir_listings
        for name in names
        # like glob, skip hidden files
        if job_str in name and not name.startswith(".") and regex.match(name)
    ]


# Run pipeline report
print("---------------\nPIPELINE REPORT\n---------------\n")
with ThreadPoolExecutor(max_workers=N_READ_THREADS) as executor:
    for job in workflow:
        print(job + ":")
        total = find_files("wrapper_*." + job + ".*sh", job)
        logged = find_files("*." + job + ".*log*", job)
        done = set(find_files("*." + job + ".*out", job))
        log_lines = dict(zip(logged, executor.map(read_first_and_last_lines, logged)))
        logged = filter_errors(logged, log_lines)
        average_runtime, total_runtime, nRunning, nErrored, nTimedOut = (
            inspect_log_files(logged, done, log_lines)
        )

        print(f"Average per-job (non-trivial) runtime: {average_runtime:.2f} minutes")
        print(f"Total runtime: {total_runtime:.2f} hours")
        print(
            f"{len(total)}\t|\t{len(done)}\t|\t{nRunning}\t|\t{nErrored}\t|\t{nTimedOut}"
        )
        print("total\t|\tdone\t|\trunning\t|\terrored\t|\ttimed out\n\n")
