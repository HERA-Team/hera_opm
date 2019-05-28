# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License

from __future__ import print_function, division, absolute_import

import os
import re
import sys
import time
import gzip
import shutil
import subprocess
import warnings
import six
from six.moves import range, map, zip
import glob
import toml


def get_jd(filename):
    """
    Get the JD from a data file name.

    Args:
    ====================
    filename (str) -- file name; assumed to follow standard convention where name is
        `zen.xxxxxxx.xxxxx.uv` (potentially with polarization and subarray information mixed in).

    Returns:
    ====================
    jd (str) -- the integer JD (fractional part truncated) as a string
    """
    m = re.match(r"zen\.([0-9]{7})\.[0-9]{5}\.", filename)
    return m.groups()[0]


def _interpolate_config(config, entry):
    """
    Interpolate entries in the configuration file.

    Args:
    ====================
    config -- a dict of the processed config file
    entry -- the raw entry in the config file to be processed

    Returns:
    ====================
    entry -- a config entry that has been interpolated

    Notes:
    ====================
    The interpolation will be invoked for strings matching the pattern:
        ${Header:Key}
    This will match an entry in the config file of the form:
        [Header]
        Key = value
    The entry "value" will be returned. If "Key" is not found in the parsed
    config file, an error is raised.
    """
    m = re.match(r"\$\{(.+)\}", str(entry))
    if m is not None:
        value = m.groups()[0]
        header, key = value.split(":")
        try:
            return config[header][key]
        except KeyError:
            raise ValueError(
                "Option {0} under header {1} was not found when "
                "processing config file".format(key, header)
            )
    else:
        return entry


def get_config_entry(config, header, item, required=True, interpolate=True):
    """
    Helper function to extract specific entry from config file.

    Args:
    ====================
    config -- a dict of a config file that has already been processed
    header (str) -- the entry in a config file to get the item of, e.g., 'OMNICAL'
    item (str) -- the attribute to retreive, e.g., 'prereqs'
    required (bool) -- whether the attribute is required or not. If required and not present,
        an error is raised. Default is True
    interpolate (bool) -- whether to interpolate the entry with an option found elsewhere in
        the config file. Interpolation is triggered by a string with the template "${header:item}".
        If the corresponding key is not defined in that part of the config file, an error is raised.
        Default is True.

    Returns:
    ====================
    entries -- a list of entries contained in the config file. If item is not present, and
        required is False, an empty list is returned.
    """
    if item in config[header]:
        entries = config[header][item]
        if interpolate:
            # if we have a list, interpolate for each element
            if isinstance(entries, list):
                for i, entry in enumerate(entries):
                    entries[i] = _interpolate_config(config, entry)
            else:
                entries = _interpolate_config(config, entries)
        return entries
    else:
        if not required:
            return None
        else:
            raise AttributeError(
                'Error processing config file: item "{0}" under header "{1}" is '
                "required, but not specified".format(item, header)
            )


def make_outfile_name(obsid, action, pol_list=[]):
    """
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
    """
    outfiles = []
    if len(pol_list) > 1 and pol_list[0] is not None:
        for pol in pol_list:
            of = "{0}.{1}.{2}.out".format(obsid, action, pol)
            outfiles.append(of)
    else:
        of = "{0}.{1}.out".format(obsid, action)
        outfiles.append(of)
    return outfiles


def make_time_neighbor_outfile_name(obsid, action, obsids, pol=None, n_neighbors="1"):
    """
    Make a list of neighbors in time for prereqs.

    Args:
    ====================
    obsid (str) -- obsid of the current file
    action (str) -- the action corresponding to the time prereqs
    obsids -- list of all obsids for the given day; uses this list (sorted) to
        define neighbors
    pol (str) -- if present, polarization string to specify for output file
    n_neighbors (str) -- number of neighboring time files to append to list.
        If set to the string "all", then all neighbors from that JD are added.

    Returns:
    ====================
    outfiles -- a list of files for time-adjacent neighbors.
    """
    outfiles = []

    # extract the integer JD of the current file
    jd = get_jd(obsid)

    # find the neighbors of current obsid in list of obsids
    # need to get just the filename, and just ones on the same day
    obsids = sorted(
        [
            os.path.basename(os.path.abspath(o))
            for o in obsids
            if jd in os.path.basename(os.path.abspath(o))
        ]
    )
    try:
        obs_idx = obsids.index(obsid)
    except ValueError:
        raise ValueError("obsid {} not found in list of obsids".format(obsid))

    if n_neighbors == "all":
        i0 = 0
        i1 = len(obsids)
    else:
        # assume we got an integer as a string; try to make sense of it
        try:
            n_neighbors = int(n_neighbors)
        except ValueError:
            raise ValueError("n_neighbors must be parsable as an int")
        if n_neighbors <= 0:
            raise ValueError("n_neighbors must be a postitive integer")
        # get n_neighbors before and after; make sure we don't have an IndexError
        i0 = max(obs_idx - n_neighbors, 0)
        i1 = min(obs_idx + n_neighbors + 1, len(obsids))

    # build list of output files to wait for
    for i in range(i0, i1):
        outfiles.append(obsids[i])

    # finalize the names of files
    if pol is None:
        for i, of in enumerate(outfiles):
            of = "{0}.{1}.out".format(of, action)
            outfiles[i] = of
    else:
        for i, of in enumerate(outfiles):
            of = "{0}.{1}.{2}.out".format(of, action, pol)
            outfiles[i] = of

    return outfiles


def process_batch_options(
    mem, ncpu=None, pbs_mail_user="youremail@example.org", queue="hera"
):
    """
    Form a series of PBS batch options to be passed to makeflow.

    Args:
    ====================
    mem (str) -- amount of memory to reserve for the task, in MB
    ncpu (str) -- number of processors to reserve
    pbs_mail_user (str) -- email address to send PBS reports to
    queue (str) -- name of PBS queue to submit to; defaults to "hera"

    Returns:
    ====================
    batch_options (str) -- series of batch options that will be parsed by makeflow; should be
        added to the makeflow file with the syntax:
            "export BATCH_OPTIONS = {batch_options}"
    """
    batch_options = "-l vmem={0:d}M,mem={0:d}M".format(mem)
    if ncpu is not None:
        batch_options += ",nodes=1:ppn={:d}".format(ncpu)
    if pbs_mail_user is not None:
        batch_options += " -M {}".format(pbs_mail_user)
    if queue is not None:
        batch_options += " -q {}".format(queue)
    return batch_options


def prep_args(args, obsid, pol=None, obsids=None):
    """
    Substitute the polarization string in a filename/obsid with the specified one.

    Args:
    ====================
    args (str) -- string containing the arguments where polarization and mini-language
        is to be substituted.
    obsid (str) -- string of filename/obsid.
    pol (str) -- polarization to substitute for the one found in obsid.
    obsids -- full list of obsids; optional, but required when time-adjacent neighbors are desired.

    Returns:
    ====================
    output (str) -- `args` string with mini-language and polarization substitutions.
    """
    if pol is not None:
        # replace pol if present
        match = re.search(r"zen\.\d{7}\.\d{5}\.(.*?)\.", obsid)
        if match:
            obs_pol = match.group(1)
            basename = re.sub(obs_pol, pol, obsid)
        else:
            basename = obsid
        # replace {basename} with actual basename
        args = re.sub(r"\{basename\}", basename, args)

    else:
        basename = obsid
        args = re.sub(r"\{basename\}", basename, args)

    # also replace time-adjacent basenames if requested
    if re.search(r"\{prev_basename\}", args):
        # check that there is an adjacent obsid to substitute
        if obsids is None:
            raise ValueError(
                "when requesting time-adjacent obsids, obsids must be provided"
            )
        jd = get_jd(obsid)
        oids = sorted(
            [
                os.path.basename(os.path.abspath(o))
                for o in obsids
                if jd in os.path.basename(os.path.abspath(o))
            ]
        )
        try:
            obs_idx = oids.index(obsid)
        except ValueError:
            raise ValueError("{} not found in list of obsids".format(obsid))
        if obs_idx == 0:
            args = re.sub(r"\{prev_basename\}", "None", args)
        else:
            args = re.sub(r"\{prev_basename\}", oids[obs_idx - 1], args)

    if re.search(r"\{next_basename\}", args):
        # check that there is an adjacent obsid to substitute
        if obsids is None:
            raise ValueError(
                "when requesting time-adjacent obsids, obsids must be provided"
            )
        jd = get_jd(obsid)
        oids = sorted(
            [
                os.path.basename(os.path.abspath(o))
                for o in obsids
                if jd in os.path.basename(os.path.abspath(o))
            ]
        )
        try:
            obs_idx = oids.index(obsid)
        except ValueError:
            raise ValueError("{} not found in list of obsids".format(obsid))
        if obs_idx == len(oids) - 1:
            args = re.sub(r"\{next_basename\}", "None", args)
        else:
            args = re.sub(r"\{next_basename\}", oids[obs_idx + 1], args)

    return args


def build_makeflow_from_config(
    obsids, config_file, mf_name=None, work_dir=None, **kwargs
):
    """
    Function for constructing a makeflow from a config file.

    Args:
    ====================
    obsids (str) -- list of paths to obsids/filenames for processing
    config_file (str) -- path to configuration file (str)
    mf_name (str) -- name of makeflow file. Defaults to "<config_file_basename>.mf" if not
        specified.
    work_dir (str) -- path to the "work directory" where all of the wrapper scripts and log
        files will be made. Defaults to the current directory.

    Returns:
    ====================
    None


    Notes:
    ====================
    This function will read the "makeflow_type" entry under the "[Options]" header to
    determine if the config file specifies an "analysis" type or "lstbin" type, and
    call the appropriate funciton below.
    """
    if isinstance(config_file, str):
        # read in config file
        config = toml.load(config_file)
    else:
        raise ValueError("config must be a path to a TOML config file")

    makeflow_type = get_config_entry(config, "Options", "makeflow_type", required=True)
    if makeflow_type == "analysis":
        build_analysis_makeflow_from_config(
            obsids, config_file, mf_name=mf_name, work_dir=work_dir, **kwargs
        )
    elif makeflow_type == "lstbin":
        build_lstbin_makeflow_from_config(
            config_file, mf_name=mf_name, work_dir=work_dir, **kwargs
        )
    else:
        raise ValueError(
            "unknown makeflow_type {} specified; must be 'analysis' or 'lstbin'".format(
                makeflow_type
            )
        )

    return


def build_analysis_makeflow_from_config(
    obsids, config_file, mf_name=None, work_dir=None
):
    """
    Construct a makeflow file from a config file.

    Args:
    ====================
    obsids (str) -- list of paths to obsids/filenames for processing
    config_file (str) -- path to configuration file
    mf_name (str) -- name of makeflow file. Defaults to "<config_file_basename>.mf" if not
        specified.
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


    Mini-language for replacement (example):
    "{basename}" = "zen.2458000.12345.uv"

    "{prev_basename}" and "{next_basename}" are previous and subsequent files adjacent to
    "{basename}", useful for specifying prereqs in time

    """
    config = toml.load(config_file)
    workflow = get_config_entry(config, "WorkFlow", "actions")

    # get general options
    pol_list = get_config_entry(config, "Options", "pols", required=False)
    if pol_list is None:
        # make a dummy list of length 1, to ensure we perform actions later
        pol_list = [None]
    else:
        # make sure that we were only passed in a single polarization in our obsids
        for i, obsid in enumerate(obsids):
            match = re.search(r"zen\.\d{7}\.\d{5}\.(.*?)\.", obsid)
            if match:
                obs_pol = match.group(1)
            else:
                raise AssertionError(
                    "Polarization not detected for input" " obsid {}".format(obsid)
                )
            for j in range(i + 1, len(obsids)):
                obsid2 = obsids[j]
                match2 = re.search(r"zen\.\d{7}\.\d{5}\.(.*?)\.", obsid2)
                if match2:
                    obs_pol2 = match2.group(1)
                    if obs_pol != obs_pol2:
                        raise AssertionError(
                            "Polarizations do not match for"
                            " obsids {} and {}".format(obsid, obsid2)
                        )

    path_to_do_scripts = get_config_entry(config, "Options", "path_to_do_scripts")
    conda_env = get_config_entry(config, "Options", "conda_env", required=False)
    source_script = get_config_entry(config, "Options", "source_script", required=False)
    pbs_mail_user = get_config_entry(config, "Options", "pbs_mail_user", required=False)
    timeout = get_config_entry(config, "Options", "timeout", required=False)
    if timeout is not None:
        # check that the `timeout' command exists on the system
        try:
            out = subprocess.check_output(["timeout", "--help"])
        except OSError:
            warnings.warn(
                'A value for the "timeout" option was specified,'
                " but the `timeout' command does not appear to be"
                " installed. Please install or remove the option"
                " from the config file"
            )
        timeout = timeout

    # open file for writing
    cf = os.path.basename(config_file)
    if mf_name is not None:
        fn = mf_name
    else:
        base, ext = os.path.splitext(cf)
        fn = "{0}.mf".format(base)

    # get the work directory
    if work_dir is None:
        work_dir = os.getcwd()
    else:
        work_dir = os.path.abspath(work_dir)
    makeflowfile = os.path.join(work_dir, fn)

    # write makeflow file
    with open(makeflowfile, "w") as f:
        # add comment at top of file listing date of creation and config file name
        dt = time.strftime("%H:%M:%S on %d %B %Y")
        print("# makeflow file generated from config file {}".format(cf), file=f)
        print("# created at {}".format(dt), file=f)

        # add resource information
        base_mem = get_config_entry(config, "Options", "base_mem", required=True)
        base_cpu = get_config_entry(config, "Options", "base_cpu", required=False)

        for obsid in obsids:
            # get parent directory
            abspath = os.path.abspath(obsid)
            parent_dir = os.path.dirname(abspath)
            filename = os.path.basename(abspath)

            # loop over actions for this obsid
            for ia, action in enumerate(workflow):
                # start list of input files
                infiles = []

                # get dependencies
                prereqs = get_config_entry(config, action, "prereqs", required=False)
                if prereqs is not None:
                    if not isinstance(prereqs, list):
                        prereqs = [prereqs]
                    for prereq in prereqs:
                        try:
                            ip = workflow.index(prereq)
                        except ValueError:
                            raise ValueError(
                                'Prereq "{0}" for action "{1}" not found in main '
                                "workflow".format(prereq, action)
                            )
                        outfiles = make_outfile_name(filename, prereq, pol_list)
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
                        # we might already have the output in the list if the
                        # previous step is a prereq
                        if of not in infiles:
                            infiles.append(of)

                # make argument list
                args = get_config_entry(config, action, "args", required=False)
                if not isinstance(args, list):
                    args = [args]
                args = " ".join(list(map(str, args)))

                # make outfile name
                outfiles = make_outfile_name(filename, action, pol_list)

                # get processing options
                mem = get_config_entry(config, action, "mem", required=False)
                ncpu = get_config_entry(config, action, "ncpu", required=False)
                if mem is None:
                    mem = base_mem
                if ncpu is None:
                    if base_cpu is not None:
                        ncpu = base_cpu

                batch_options = process_batch_options(mem, ncpu, pbs_mail_user)
                print("export BATCH_OPTIONS = {}".format(batch_options), file=f)

                # make rules
                for pol, outfile in zip(pol_list, outfiles):
                    time_prereqs = get_config_entry(
                        config, action, "time_prereqs", required=False
                    )
                    if time_prereqs is not None:
                        if not isinstance(time_prereqs, list):
                            time_prereqs = [time_prereqs]
                        # get how many neighbors we should be including
                        n_neighbors = get_config_entry(
                            config, action, "n_time_neighbors", required=True
                        )

                        # get a copy of the infile list; we're going to add to it, but don't want these
                        # entries broadcast across pols
                        infiles_pol = infiles
                        for tp in time_prereqs:
                            try:
                                ip = workflow.index(tp)
                            except ValueError:
                                raise ValueError(
                                    'Time prereq "{0}" for action "{1}" not found in main '
                                    "workflow".format(tp, action)
                                )
                            # add neighbors for all pols
                            for pol2 in pol_list:
                                tp_outfiles = make_time_neighbor_outfile_name(
                                    filename, tp, obsids, pol2, n_neighbors
                                )
                                for of in tp_outfiles:
                                    infiles_pol.append(of)

                        # replace '{basename}' with actual filename
                        # also replace polarization string, and time neighbors
                        prepped_args = prep_args(args, filename, pol, obsids)
                    else:
                        # just get a copy of the infiles as-is
                        infiles_pol = infiles
                        # replace '{basename}' with actual filename
                        # aslo replace polarization string
                        prepped_args = prep_args(args, filename, pol)

                    # make logfile name
                    # logfile will capture stdout and stderr
                    logfile = re.sub(r"\.out", ".log", outfile)
                    logfile = os.path.join(work_dir, logfile)

                    # make a small wrapper script that will run the actual command
                    # can't embed if; then statements in makeflow script
                    wrapper_script = re.sub(r"\.out", ".sh", outfile)
                    wrapper_script = "wrapper_{}".format(wrapper_script)
                    wrapper_script = os.path.join(work_dir, wrapper_script)
                    with open(wrapper_script, "w") as f2:
                        print("#!/bin/bash", file=f2)
                        if source_script is not None:
                            print("source {}".format(source_script), file=f2)
                        if conda_env is not None:
                            print("conda activate {}".format(conda_env), file=f2)
                        print("date", file=f2)
                        print("cd {}".format(parent_dir), file=f2)
                        if timeout is not None:
                            print(
                                "timeout {0} {1} {2}".format(
                                    timeout, command, prepped_args
                                ),
                                file=f2,
                            )
                        else:
                            print("{0} {1}".format(command, prepped_args), file=f2)
                        print("if [ $? -eq 0 ]; then", file=f2)
                        print("  cd {}".format(work_dir), file=f2)
                        print("  touch {}".format(outfile), file=f2)
                        print("else", file=f2)
                        print(
                            "  mv {0} {1}".format(logfile, logfile + ".error"), file=f2
                        )
                        print("fi", file=f2)
                        print("date", file=f2)
                    # make file executable
                    os.chmod(wrapper_script, 0o755)

                    # first line lists target file to make (dummy output file), and requirements
                    # second line is "build rule", which runs the shell script and makes the output file
                    infiles_pol = " ".join(infiles_pol)
                    line1 = "{0}: {1}".format(outfile, infiles_pol)
                    line2 = "\t{0} > {1} 2>&1\n".format(wrapper_script, logfile)
                    print(line1, file=f)
                    print(line2, file=f)

                # save previous outfiles for next time
                outfiles_prev = outfiles

    return


def build_lstbin_makeflow_from_config(
    config_file, mf_name=None, work_dir=None, **kwargs
):
    """
    Function for constructing an LST-binning makeflow file from input data and a config_file.

    Arguments:
    ====================
    config_file (str) -- path to config file containing options
    mf_name (str) -- name of makeflow file. Defaults to "<config_file_basename>.mf" if not
        specified.

    Returns:
    ====================
    None


    Notes:
    ====================
    The major difference between this function and the one above is the use of the `config_lst_bin_files`
    function from hera_cal, which is used to determine the number of output files, which are parallelized
    over in the makeflow.
    """
    # import hera_cal
    from hera_cal import lstbin

    # read in config file
    config = toml.load(config_file)
    cf = os.path.basename(config_file)

    # get LSTBIN arguments
    lstbin_args = get_config_entry(config, "LSTBIN", "args", required=False)

    # set output_file_select to None
    config["LSTBIN_OPTS"]["output_file_select"] = str("None")

    # get general options
    pol_list = get_config_entry(config, "Options", "pols", required=False)
    if not isinstance(pol_list, list):
        pol_list = [pol_list]
    path_to_do_scripts = get_config_entry(config, "Options", "path_to_do_scripts")
    conda_env = get_config_entry(config, "Options", "conda_env", required=False)
    source_script = get_config_entry(config, "Options", "source_scriopt", required=False)
    timeout = get_config_entry(config, "Options", "timeout", required=False)
    if timeout is not None:
        # check that the `timeout' command exists on the system
        try:
            out = subprocess.check_output(["timeout", "--help"])
        except OSError:
            warnings.warn(
                'A value for the "timeout" option was specified,'
                " but the `timeout' command does not appear to be"
                " installed. Please install or remove the option"
                " from the config file"
            )

    # open file for writing
    if mf_name is not None:
        fn = mf_name
    else:
        base, ext = os.path.splitext(cf)
        fn = "{0}.mf".format(base)

    # determine whether or not to parallelize
    parallelize = get_config_entry(config, "LSTBIN_OPTS", "parallelize", required=True)
    if "parent_dir" in kwargs:
        parent_dir = kwargs["parent_dir"]
    else:
        parent_dir = get_config_entry(
            config, "LSTBIN_OPTS", "parent_dir", required=True
        )
    if work_dir is None:
        work_dir = parent_dir
    makeflowfile = os.path.join(work_dir, fn)

    # define command
    command = "do_LSTBIN.sh"
    command = os.path.join(path_to_do_scripts, command)

    # write makeflow file
    with open(makeflowfile, "w") as f:
        # add comment at top of file listing date of creation and config file name
        dt = time.strftime("%H:%M:%S on %d %B %Y")
        print("# makeflow file generated from config file {}".format(cf), file=f)
        print("# created at {}".format(dt), file=f)

        # add resource information
        base_mem = get_config_entry(config, "Options", "base_mem", required=True)
        base_cpu = get_config_entry(config, "Options", "base_cpu", required=False)
        pbs_mail_user = get_config_entry(
            config, "Options", "pbs_mail_user", required=False
        )
        batch_options = process_batch_options(base_mem, base_cpu, pbs_mail_user)
        print("export BATCH_OPTIONS = {}".format(batch_options), file=f)

        # loop over polarizations
        for pol in pol_list:
            # get data files and substitute w/ pol
            datafiles = get_config_entry(
                config, "LSTBIN_OPTS", "data_files", required=True
            )
            # strip extra quotations if present
            datafiles = [df.strip("'").strip('"') for df in datafiles]
            if pol is not None:
                datafiles = [df.format(pol=pol) for df in datafiles]
            datafiles = [os.path.join(parent_dir, df) for df in datafiles]

            # get number of output files for this pol
            if parallelize:
                # get LST-specific config options
                dlst = get_config_entry(config, "LSTBIN_OPTS", "dlst", required=True)
                if dlst == "None":
                    dlst = None
                else:
                    dlst = float(dlst)
                lst_start = float(
                    get_config_entry(config, "LSTBIN_OPTS", "lst_start", required=True)
                )
                fixed_lst_start = bool(
                    get_config_entry(
                        config, "LSTBIN_OPTS", "fixed_lst_start", required=True
                    )
                )
                ntimes_per_file = int(
                    get_config_entry(
                        config, "LSTBIN_OPTS", "ntimes_per_file", required=True
                    )
                )

                # pre-process files to determine the number of output files
                _datafiles = [sorted(glob.glob(df)) for df in datafiles]
                if six.PY2:
                    _datafiles = [
                        [df.encode("utf-8") for df in li] for li in _datafiles
                    ]

                output = lstbin.config_lst_bin_files(
                    _datafiles,
                    dlst=dlst,
                    lst_start=lst_start,
                    fixed_lst_start=fixed_lst_start,
                    ntimes_per_file=ntimes_per_file,
                )
                nfiles = len(output[2])
            else:
                nfiles = 1

            # loop over output files
            for output_file_index in range(nfiles):
                # if parallize, update output_file_select
                if parallelize:
                    config["LSTBIN_OPTS"]["output_file_select"] = str(output_file_index)

                # make outfile list
                if pol is not None:
                    polstr = ".{}".format(pol)
                else:
                    polstr = ""
                outfile = "lstbin_outfile_{}.{}{}.out".format(
                    output_file_index, "LSTBIN", polstr
                )

                # get args list for lst-binning step
                _args = [
                    get_config_entry(config, "LSTBIN_OPTS", a, required=True)
                    for a in lstbin_args
                ]
                args = []
                for a in _args:
                    args.append(str(a))

                # extend datafiles
                args.extend(datafiles)

                # turn into string
                args = " ".join(args)

                # make logfile name
                # logfile will capture stdout and stderr
                logfile = re.sub(r"\.out", ".log", outfile)
                logfile = os.path.join(work_dir, logfile)

                # make a small wrapper script that will run the actual command
                # can't embed if; then statements in makeflow script
                wrapper_script = re.sub(r"\.out", ".sh", outfile)
                wrapper_script = "wrapper_{}".format(wrapper_script)
                wrapper_script = os.path.join(work_dir, wrapper_script)
                with open(wrapper_script, "w") as f2:
                    print("#!/bin/bash", file=f2)
                    if source_script is not None:
                        print("source {}".format(source_script, file=f2))
                    if conda_env is not None:
                        print("conda activate {}".format(conda_env), file=f2)
                    print("date", file=f2)
                    print("cd {}".format(parent_dir), file=f2)
                    if timeout is not None:
                        print(
                            "timeout {0} {1} {2}".format(timeout, command, args),
                            file=f2,
                        )
                    else:
                        print("{0} {1}".format(command, args), file=f2)
                    print("if [ $? -eq 0 ]; then", file=f2)
                    print("  cd {}".format(work_dir), file=f2)
                    print("  touch {}".format(outfile), file=f2)
                    print("fi", file=f2)
                    print("date", file=f2)
                # make file executable
                os.chmod(wrapper_script, 0o755)

                # first line lists target file to make (dummy output file), and requirements
                # second line is "build rule", which runs the shell script and makes the output file
                line1 = "{0}: {1}".format(outfile, command)
                line2 = "\t{0} > {1} 2>&1\n".format(wrapper_script, logfile)
                print(line1, file=f)
                print(line2, file=f)

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
    wrapper_files = [
        fn for fn in files if fn[:8] == "wrapper_" or fn[-8:] == ".wrapper"
    ]

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


def consolidate_logs(
    work_dir, output_fn, overwrite=False, remove_original=True, zip_file=False
):
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
            raise IOError(
                "Error: output file {} found; set overwrite=True to overwrite".format(
                    output_fn
                )
            )
    # also check for the zipped file if it exists when we specify zip_file
    if zip_file:
        gzip_fn = output_fn + ".gz"
        if os.path.exists(gzip_fn):
            if overwrite:
                print("Overwriting output file {}".format(gzip_fn))
                os.remove(gzip_fn)
            else:
                raise IOError(
                    "Error: output file {} found; set overwrite=True to overwrite".format(
                        gzip_fn
                    )
                )

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
