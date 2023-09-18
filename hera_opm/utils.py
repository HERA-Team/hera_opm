# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Module for generating ArgumentParsers."""

import argparse
import os


# argument-generating functions for scripts
def get_makeflow_ArgumentParser():
    """Get an ArgumentParser instance for building makeflow files from config files.

    Parameters
    ----------
    None

    Returns
    -------
    ap : ArgumentParser instance
        A parser suitable for interpreting the desired arguments.
    """
    ap = argparse.ArgumentParser()

    # set relevant properties
    ap.prog = "build_makeflow_from_config.py"
    ap.add_argument(
        "-c",
        "--config",
        default="",
        type=str,
        help="Full path to config file defining workflow. Default is ''",
    )
    ap.add_argument(
        "-o",
        "--output",
        default=None,
        type=str,
        help="Full path to the output file. Default is None (so output is <config_basename>.mf)",
    )
    ap.add_argument(
        "files",
        metavar="files",
        type=str,
        nargs="*",
        default=[],
        help="Files to apply the pipeline to. Typically raw miriad files.",
    )
    ap.add_argument(
        "--scan-files",
        action="store_true",
        default=False,
        help="Scan metadata of HERA data files before including in workflow. Requires pyuvdata",
    )
    ap.add_argument(
        "--rename-bad-files",
        action="store_true",
        default=False,
        help="Rename files with bad metadata (found with --scan-files) with suffix set by --bad-suffix (default is '.METADATA_ERROR').",
    )
    ap.add_argument(
        "--bad-suffix",
        default=".METADATA_ERROR",
        type=str,
        help="String to append to files pyuvdata could not read after running with --scan-files with --rename-bad-files. Default '.METADATA_ERROR'.",
    )
    ap.add_argument(
        "-d",
        "--work-dir",
        default=None,
        help="Directory into which all wrappers and makeflow file will be written.",
        type=str,
    )
    return ap


def get_cleaner_ArgumentParser(clean_func):
    """Get an ArgumentParser instance for clean up functions.

    Parameters
    ----------
    clean_func : str
        The name of the cleaner function to get arguments for. Must be one of:
        "wrapper", "output", "logs".

    Returns
    -------
    ap : ArgumentParser instance
        A parser with the relevant options.

    Raises
    ------
    AssertionError
        This is raised if `clean_func` is not a valid option.

    """
    ap = argparse.ArgumentParser()

    # check that function specified is a valid option
    functions = ["wrapper", "output", "logs"]
    if clean_func not in functions:
        raise AssertionError("clean_func must be one of {}".format(",".join(functions)))

    # choose options based on script name
    if clean_func == "wrapper":
        ap.prog = "clean_wrapper_scripts.py"
        ap.add_argument(
            "directory",
            type=str,
            nargs="?",
            default=os.getcwd(),
            help="Directory where wrapper files reside. Defaults to current directory.",
        )

    elif clean_func == "output":
        ap.prog = "clean_output_files.py"
        ap.add_argument(
            "directory",
            type=str,
            nargs="?",
            default=os.getcwd(),
            help="Directory where output files reside. Defaults to current directory.",
        )

    elif clean_func == "logs":
        ap.prog = "consolidate_logs.py"
        ap.add_argument(
            "directory",
            type=str,
            nargs="?",
            default=os.getcwd(),
            help="Directory where log files reside. Defaults to current directory.",
        )
        ap.add_argument(
            "-o",
            "--output",
            default="mf.log",
            type=str,
            help="Name of output file. Default is 'mf.log'",
        )
        ap.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help="Option to overwrite output file if it already exists.",
        )
        ap.add_argument(
            "--save_original",
            action="store_false",
            dest="remove_original",
            default=True,
            help="Save original log files once combined in output.",
        )
        ap.add_argument(
            "-z",
            "--zip",
            action="store_true",
            default=False,
            help="Option to zip resulting output file.",
        )

    return ap
