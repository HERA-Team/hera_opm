# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License

from __future__ import print_function, division, absolute_import

import argparse
import os


# argument-generating functions for scripts
def get_makeflow_ArgumentParser():
    """
    Function for getting an ArgumentParser instance for building makeflow files from config files.

    Arguments:
    ====================
    None

    Returns:
    ====================
    a -- an argparse.ArgumentParser instance with the relevant options
    """
    a = argparse.ArgumentParser()

    # set relevant properties
    a.prog = "build_makeflow_from_config.py"
    a.add_argument(
        "-c",
        "--config",
        default="",
        type=str,
        help="Full path to config file defining workflow. Default is ''",
    )
    a.add_argument(
        "-o",
        "--output",
        default=None,
        type=str,
        help="Full path to the output file. Default is None (so output is <config_basename>.mf)",
    )
    a.add_argument(
        "files",
        metavar="files",
        type=str,
        nargs="*",
        default=[],
        help="Files to apply the pipeline to. Typically raw miriad files.",
    )

    return a


def get_cleaner_ArgumentParser(clean_func):
    """
    Function for getting an ArgumentParser instance for clean up functions.

    Arguments:
    ====================
    clean_func (str) -- name of the cleaner function to get arguments for.

    Returns:
    ====================
    a -- an argparse.ArgumentParser instance with the relevant options
    """
    a = argparse.ArgumentParser()

    # check that function specified is a valid option
    functions = ["wrapper", "output", "logs"]
    if clean_func not in functions:
        raise AssertionError("clean_func must be one of {}".format(",".join(functions)))

    # choose options based on script name
    if clean_func == "wrapper":
        a.prog = "clean_wrapper_scripts.py"
        a.add_argument(
            "directory",
            type=str,
            nargs="?",
            default=os.getcwd(),
            help="Directory where wrapper files reside. Defaults to current directory.",
        )

    elif clean_func == "output":
        a.prog = "clean_output_files.py"
        a.add_argument(
            "directory",
            type=str,
            nargs="?",
            default=os.getcwd(),
            help="Directory where output files reside. Defaults to current directory.",
        )

    elif clean_func == "logs":
        a.prog = "consolidate_logs.py"
        a.add_argument(
            "directory",
            type=str,
            nargs="?",
            default=os.getcwd(),
            help="Directory where log files reside. Defaults to current directory.",
        )
        a.add_argument(
            "-o",
            "--output",
            default="mf.log",
            type=str,
            help="Name of output file. Default is 'mf.log'",
        )
        a.add_argument(
            "--overwrite",
            action="store_true",
            default=False,
            help="Option to overwrite output file if it already exists.",
        )
        a.add_argument(
            "--save_original",
            action="store_false",
            dest="remove_original",
            default=True,
            help="Save original log files once combined in output.",
        )
        a.add_argument(
            "-z",
            "--zip",
            action="store_true",
            default=False,
            help="Option to zip resulting output file.",
        )

    return a
