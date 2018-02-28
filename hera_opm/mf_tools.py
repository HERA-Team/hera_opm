# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration

from __future__ import print_function, division, absolute_import
import os
import re
import sys
import time
import gzip
import shutil
import ConfigParser as configparser
from configparser import ConfigParser, ExtendedInterpolation


def get_config_entry(config, header, item, required=True):
    '''
    Helper function to extract specific entry from config file.

    Args:
    ====================
    config -- a ConfigParser object that has read in the config file
    header (str) -- the entry in a config file to get the item of, e.g., 'OMNICAL'
    item (str) -- the attribute to retreive, e.g., 'prereqs'
    required (bool) -- whether the attribute is required or not. If required and not present,
        an error is raised.

    Returns:
    ====================
    entries -- a list of entries contained in the config file. If item is not present, and 
        required is False, an empty list is returned.
    '''
    if config.has_option(header, item):
        entries = config.get(header, item).split(',')
        entries = [entry.strip() for entry in entries]
        return entries
    else:
        if not required:
            return []
        else:
            raise AttributeError("Error processing config file: item \"{0}\" under header \"{1}\" is "
                                 "required, but not specified".format(item, header))


def make_outfile_name(obsid, action, pol_list=[]):
    '''
    Make a list of unique output files names for each stage and polarization.

    Args:
    ====================
    obsid (str) -- obsid of the file
    action (str) -- the action corresponding to the output name
    pol_list -- a list of strings for polarizations in files; if an empty list,
        then all polarizations in a single file is assumed. (Default empty list)

    Returns:
    ====================
    outfiles -- a list of files that represent output produced for `action`
        corresponding to `obsid`. For multiple polarizations, contains one string
        per polarization. For one or no polarizations, just a list with a single 
        entry is returned.
    '''
    outfiles = []
    if len(pol_list) > 1:
        for pol in pol_list:
            of = "{0}.{1}.{2}.out".format(obsid, action, pol)
            outfiles.append(of)
    else:
        of = "{0}.{1}.out".format(obsid, action)
        outfiles.append(of)
    return outfiles


def prep_args(args, obsid, pol):
    '''
    Substitute the polarization string in a filename/obsid with the specified one.

    Args:
    ====================
    args (str) -- string containing the arguments where polarization and mini-language
        is to be substituted.
    obsid (str) -- string of filename/obsid.
    pol (str) -- polarization to substitute for the one found in obsid.

    Returns:
    ====================
    output (str) -- `args` string with mini-language and polarization substitutions.
    '''
    # replace pol if present
    match = re.search(r'zen\.\d{7}\.\d{5}\.(.+)\.', obsid)
    if match:
        obs_pol = match.group(1)
        basename = re.sub(obs_pol, pol, obsid)
    else:
        basename = obsid
    # replace {basename} with actual basename
    return re.sub(r'\{basename\}', basename, args)


def build_makeflow_from_config(obsids, config_file, mf_name=None, work_dir=None):
    '''
    Construct a makeflow file from a config file.

    Args:
    ====================
    obsids (str) -- path to obsids/filenames for processing
    config_file (str) -- path to configuration file
    mf_name (str) -- name of makeflow file. Note that this is just the prefix, as the full
        makeflow filename also includes the name of the config file, and the proper suffix.
        Defaults to current UNIX time, to avoid naming conflicts.
    work_dir (str) -- path to the "work directory" where all of the wrapper scripts and log
        files will be made. Defaults to the current directory.

    Returns:
    ====================
    None


    Notes:
    ====================

    Config file structure:

    [STAGENAME]
    prereqs = STAGENAME1, STAGENAME2
    args = arg1, arg2
    ncpu = 1
    mem = 5000 (MB)


    Mini-language for replacement:
    basename = "zen.2458000.12345.uv"

    '''
    # read in config file
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_file) 
    workflow = get_config_entry(config, 'WorkFlow', 'actions')

    # get general options
    pol_list = get_config_entry(config, 'Options', 'pols', required=False)
    if len(pol_list) == 0:
        # make a dummy list of length 1, to ensure we perform actions later
        pol_list = ['']
    path_to_do_scripts = get_config_entry(config, 'Options', 'path_to_do_scripts')[0]
    conda_env = get_config_entry(config, 'Options', 'conda_env', required=False)
    if conda_env == []:
        conda_env = None

    # open file for writing
    cf = os.path.basename(config_file)
    if mf_name is not None:
        fn = "{0}.{1}.mf".format(mf_name, cf)
    else:
        t = str(int(time.time()))
        fn = "{0}.{1}.mf".format(t, cf)

    # get the work directory
    if work_dir is None:
        work_dir = os.getcwd()
    else:
        work_dir = os.path.abspath(work_dir)
    makeflowfile = os.path.join(work_dir, fn)

    # write makeflow file
    with open(makeflowfile, "w") as f:
        for obsid in obsids:
            # get parent directory
            abspath = os.path.abspath(obsid)
            parent_dir = os.path.dirname(obsid)

            # loop over actions for this obsid
            for ia, action in enumerate(workflow):
                # start list of input files
                infiles = []

                # get dependencies
                prereqs = get_config_entry(config, action, "prereqs", required=False)
                if len(prereqs) > 0:
                    for prereq in prereqs:
                        try:
                            ip = workflow.index(prereq)
                        except ValueError:
                            raise ValueError("Prereq \"{0}\" for action \"{1}\" not found in main "
                                             "workflow".format(prereq, action))
                        outfiles = make_outfile_name(obsid, prereq, pol_list)
                        for of in outfiles:
                            infiles.append(of)

                # add command to infile list
                # this implicitly checks that do_{STAGENAME}.sh script exists
                command = "do_{}.sh".format(action)
                command = os.path.join(path_to_do_scripts, command)
                infiles.append(command)

                # also add previous outfiles to input requirements
                if ia > 0:
                    for of in outfiles_prev:
                        infiles.append(of)
                infiles = ' '.join(infiles)

                # make argument list
                args = get_config_entry(config, action, "args", required=False)
                args = ' '.join(args)

                # make outfile name
                outfiles = make_outfile_name(obsid, action, pol_list)

                # make rules
                for pol, outfile in zip(pol_list, outfiles):
                    # replace '{basename}' with actual filename
                    # also replace polarization string
                    prepped_args = prep_args(args, obsid, pol)

                    # make logfile name
                    # logfile will capture stdout and stderr
                    logfile = re.sub('\.out', '.log', outfile)
                    logfile = os.path.join(work_dir, logfile)

                    # make a small wrapper script that will run the actual command
                    # can't embed if; then statements in makeflow script
                    wrapper_script = re.sub('\.out', '.sh', outfile)
                    wrapper_script = "wrapper_{}".format(wrapper_script)
                    wrapper_script = os.path.join(work_dir, wrapper_script)
                    with open(wrapper_script, "w") as f2:
                        print("#!/bin/bash", file=f2)
                        if conda_env is not None:
                            print("source activate {}".format(conda_env), file=f2)
                        print("date", file=f2)
                        print("cd {}".format(parent_dir), file=f2)
                        print("{0} {1}".format(command, prepped_args), file=f2)
                        print("if [ $? -eq 0 ]; then", file=f2)
                        print("  cd {}".format(work_dir), file=f2)
                        print("  touch {}".format(outfile), file=f2)
                        print("fi", file=f2)
                        print("date", file=f2)
                    # make file executable
                    os.chmod(wrapper_script, 0o755)

                    # first line lists target file to make (dummy output file), and requirements
                    # second line is "build rule", which runs the shell script and makes the output file
                    line1 = "{0}: {1}".format(outfile, infiles)
                    line2 = "\t{0} > {1} 2>&1\n".format(wrapper_script, logfile)
                    print(line1, file=f)
                    print(line2, file=f)

                # save previous outfiles for next time
                outfiles_prev = outfiles

    return

def clean_wrapper_scripts(work_dir):
    """
    Clean up wrapper scripts from work directory.

    This script removes any files in the specified directory that begin with "wrapper_",
    which is how the scripts are named in the 'build_makeflow_from_config' function above.
    It also removes files that end in ".wrapper", which is how makeflow labels wrapper
    scripts for batch processing.

    Arguments:
    ====================
    work_dir (str) -- the full path to the work directory

    Returns:
    ====================
    None

    """
    # list files in work directory
    files = os.listdir(work_dir)
    wrapper_files = [fn for fn in files if fn[:8] == "wrapper_" or fn[-8:] == ".wrapper"]

    # remove files; assumes individual files (and not directories)
    for fn in wrapper_files:
        abspath = os.path.join(work_dir, fn)
        os.remove(abspath)

    return

def clean_output_files(work_dir):
    """
    Clean up output files from work directory.

    The pipeline process uses empty files ending in '.out' to mark task completion.
    This script removes such files, since they are unnecessary once the pipeline is
    completed.

    Arguments:
    ====================
    work_dir (str) -- the full path to the work directory

    Returns:
    ====================
    None

    """
    # list files in work directory
    files = os.listdir(work_dir)
    output_files = [fn for fn in files if fn[-4:] == ".out"]

    # remove files; assumes individual files (and not directories)
    for fn in output_files:
        abspath = os.path.join(work_dir, fn)
        os.remove(abspath)

    return

def consolidate_logs(work_dir, output_fn, overwrite=False, remove_original=True,
                     zip_file=False):
    """
    Combine logs from a makeflow run into a single file.

    This function will combine the log files from a makeflow execution into a single file.
    It also provides the option of zipping the resulting file, to save space.

    Arguments:
    ====================
    work_dir (str) -- the full path to the work directory
    output_fn (str) -- the full path to the desired output file
    overwrite (bool) -- option to overwrite the named output_fn if it exists. Defaults to False.
    remove_original (bool) -- option to remove original individual logs. Defaults to True.
    zip_file (bool) -- option to zip the resulting file. Defaults to False.

    Returns:
    ====================
    None
    """
    # Check to see if output file already exists.
    # Note we need to check if this file exists, even when zip_file=True, since we use the standard
    # file as an intermediary before zipping, then removed.
    if os.path.exists(output_fn):
        if overwrite:
            print("Overwriting output file {}".format(output_fn))
            os.remove(output_fn)
        else:
            raise IOError("Error: output file {} found; set overwrite=True to overwrite".format(output_fn))
    # also check for the zipped file if it exists when we specify zip_file
    if zip_file:
        gzip_fn = output_fn + '.gz'
        if os.path.exists(gzip_fn):
            if overwrite:
                print("Overwriting output file {}".format(gzip_fn))
                os.remove(gzip_fn)
            else:
                raise IOError("Error: output file {} found; set overwrite=True to overwrite".format(gzip_fn))

    # list log files in work directory; assumes the ".log" suffix
    files = os.listdir(work_dir)
    log_files = [fn for fn in sorted(files) if fn[-4:] == ".log"]

    # write log file
    # echos original log filename, then adds a linebreak for separation
    with open(output_fn, "w") as f:
        for fn in log_files:
            f.write(fn + "\n")
            abspath = os.path.join(work_dir, fn)
            with open(abspath, "r") as f2:
                f.write(f2.read())
            f.write("\n")

    if remove_original:
        for fn in log_files:
            abspath = os.path.join(work_dir, fn)
            os.remove(abspath)

    if zip_file:
        # use gzip lib to compress
        with open(output_fn, "rb") as f_in, gzip.open(gzip_fn, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        # remove original file
        os.remove(output_fn)

    return

