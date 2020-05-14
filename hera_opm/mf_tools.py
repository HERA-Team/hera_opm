# -*- mode: python; coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Module for converting a config file into a makeflow script."""

import os
import re
import time
import gzip
import shutil
import subprocess
import warnings
import glob
import toml


def get_jd(filename):
    """Get the JD from a data file name.

    Parameters
    ----------
    filename : str
        File name. Assumed to follow standard convention where name is
        `zen.xxxxxxx.xxxxx.uv`.

    Returns
    -------
    str
        The integer JD (fractional part truncated).

    """
    m = re.match(r"zen\.([0-9]{7})\.[0-9]{5}\.", filename)
    return m.groups()[0]


def _interpolate_config(config, entry):
    """Interpolate entries in the configuration file.

    Parameters
    ----------
    config : dict
        The entries of the processed config file.
    entry : str
        The raw entry in the config file to be processed.

    Returns
    -------
    entry : str
        A config entry that has been interpolated.

    Notes
    -----
    The interpolation will be invoked for strings matching the pattern:
    ${Header:Key} This will match an entry in the config file of the form:
    [Header] Key = value The entry "value" will be returned. If "Key" is not
    found in the parsed config file, an error is raised.

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


def get_config_entry(config, header, item, required=True, interpolate=True,
                     total_length=1):
    """Extract a specific entry from config file.

    Parameters
    ----------
    config : dict
        Entries of a config file that has already been processed.
    header : str
        The entry in a config file to get the item of, e.g., 'OMNICAL'.
    item : str
        The attribute to retreive, e.g., 'mem'.
    required : bool
        Whether the attribute is required or not. If required and not present,
        an error is raised. Default is True.
    interpolate : bool
        Whether to interpolate the entry with an option found elsewhere in the
        config file. Interpolation is triggered by a string with the template
        "${header:item}". If the corresponding key is not defined in that part
        of the config file, an error is raised. Default is True.
    total_length : int, optional
        If this parameter belongs to the special group of
        [stride_length, n_time_neighbors],
        the entry will be further parsed to interpret 'all', and be replaced
        with (total_length - 1) // 2 if time_centered is True (default) or
        with (total_length - 1) if time_centered is False.

    Returns
    -------
    entries : list of str
        List of entries contained in the config file. If item is not present, and
        required is False, None is returned.

    Raises
    ------
    AssertionError
        This error is raised if the specified entry is required but not present.

    """
    try:
        entries = config[header][item]
        if interpolate:
            # if we have a list, interpolate for each element
            if isinstance(entries, list):
                for i, entry in enumerate(entries):
                    entries[i] = _interpolate_config(config, entry)
            else:
                entries = _interpolate_config(config, entries)
        if item in ['stride_length', 'n_time_neighbors']:
            time_centered = get_config_entry(config, header, 'time_centered',
                                             required=False)
            if entries == 'all':
                if time_centered or time_centered is None:
                    entries = str((total_length - 1) // 2)
                else:
                    entries = str(total_length - 1)
        return entries
    except KeyError:
        if not required:
            return None
        else:
            raise AssertionError(
                'Error processing config file: item "{0}" under header "{1}" is '
                "required, but not specified".format(item, header)
            )


def make_outfile_name(obsid, action):
    """Make a list of unique output files names for each stage and polarization.

    Parameters
    ----------
    obsid : str
        The obsid of the file.
    action : str
        The action corresponding to the output name.

    Returns
    -------
    outfiles : list of str
        A list of files that represent output produced for `action`
        corresponding to `obsid`.

    """
    return [f'{obsid}.{action}.out']


def sort_obsids(obsids, jd=None, return_basenames=True):
    """
    Sort obsids in a given day.

    Parameters
    ----------
    obsids : list or tuple of str
        A list of all obsids to be sorted.
    jd : str, optional
        The Julian date to include in sorted obsids. If not provided, includes
        all obsids regardless of day.
    return_basenames : bool, optional
        Whether to return only basenames of paths of obsids. Default is True.
        If False, return full path as given in input.

    Returns
    -------
    sortd_obsids : list of str
        Obsids (basename or absolute path), sorted by filename for given Julian day.
    """
    if jd is None:
        jd = ""
    # need to get just the filename, and just ones on the same day
    keys = [
        os.path.basename(os.path.abspath(o))
        for o in obsids
        if jd in os.path.basename(os.path.abspath(o))
    ]
    to_sort = list(zip(keys, range(len(obsids))))
    temp = sorted(to_sort, key=lambda obs: obs[0])
    argsort = [obs[1] for obs in temp]

    sorted_obsids = [obsids[i] for i in argsort]
    if return_basenames:
        sorted_obsids = [os.path.basename(obsid) for obsid in sorted_obsids]

    return sorted_obsids


def make_time_neighbor_outfile_name(
    obsid, action, obsids, n_time_neighbors="1", centered=None
):
    """
    Make a list of neighbors in time for prereqs.

    Parameters
    ----------
    obsid : str
        The obsid of the current file.
    action : str
        The action corresponding to the prereqs.
    obsids : list of str
        A list of all obsids for the given day; uses this list (sorted) to
        define neighbors
    n_time_neighbors : str
        Number of neighboring time files to append to list. If set to the
        string "all", then all neighbors from that JD are added.
    centered : bool, optional
        Whether the provided obsid should be in the center of the neighbors.
        If True (default), returns n_time_neighbors on either side of obsid.
        If False, returns original obsid _and_ n_time_neighbors following.

    Returns
    -------
    outfiles : list of str
        A list of files for time-adjacent neighbors.

    Raises
    ------
    ValueError
        Raised if the specified obsid is not present in the full list, if
        `n_time_neighbors` cannot be parsed as an int, or if `n_time_neighbors`
        is negative.

    """
    if centered is None:
        centered = True
    outfiles = []

    # extract the integer JD of the current file
    jd = get_jd(obsid)

    # find the neighbors of current obsid in list of obsids
    obsids = sort_obsids(obsids, jd=jd)

    try:
        obs_idx = obsids.index(obsid)
    except ValueError:
        raise ValueError("obsid {} not found in list of obsids".format(obsid))

    if n_time_neighbors == "all":
        i0 = 0
        i1 = len(obsids)
    else:
        # assume we got an integer as a string; try to make sense of it
        try:
            n_time_neighbors = int(n_time_neighbors)
        except ValueError:
            raise ValueError("n_time_neighbors must be parsable as an int")
        if n_time_neighbors <= 0:
            raise ValueError("n_time_neighbors must be a postitive integer")
        # get n_time_neighbors before and after; make sure we don't have an IndexError
        i0 = max(obs_idx - centered * n_time_neighbors, 0)
        i1 = min(obs_idx + n_time_neighbors + 1, len(obsids))

    # build list of output files to wait for
    for i in range(i0, i1):
        outfiles.append(obsids[i])

    # finalize the names of files
    outfiles = [f'{of}.{action}.out' for of in outfiles]

    return outfiles


def process_batch_options(
    mem, ncpu=None, mail_user="youremail@example.org", queue="hera", batch_system="pbs"
):
    """Form a series of batch options to be passed to makeflow.

    Parameters
    ----------
    mem : str
        Amount of memory to reserve for the task, in MB.
    ncpu : str, optional
        The number of processors to reserve.
    mail_user : str, optional
        The email address to send batch system reports to.
    queue : str, optional
        Name of queue/partition to submit to; defaults to "hera".
    batch_system : str, optional
        The batch system that will be running the makeflow. Must be one of:
        "pbs", "slurm", "htcondor".

    Returns
    -------
    batch_options : str
        Series of batch options that will be parsed by makeflow; should be
        added to the makeflow file with the syntax:
            "export BATCH_OPTIONS = {batch_options}"

    Raises
    ------
    ValueError
        Raised if batch_system is not a valid option.

    """
    if batch_system is None:
        batch_system = "pbs"
    if batch_system.lower() == "pbs":
        batch_options = "-l vmem={0:d}M,mem={0:d}M".format(mem)
        if ncpu is not None:
            batch_options += ",nodes=1:ppn={:d}".format(ncpu)
        if mail_user is not None:
            batch_options += " -M {}".format(mail_user)
        if queue is not None:
            batch_options += " -q {}".format(queue)
    elif batch_system.lower() == "slurm":
        batch_options = "--mem {:d}M".format(mem)
        if ncpu is not None:
            batch_options += " -n {:d}".format(ncpu)
        if mail_user is not None:
            batch_options += " --mail-user {}".format(mail_user)
        if queue is not None:
            batch_options += " -p {}".format(queue)
    elif batch_system.lower() == "htcondor":
        batch_options = "request_memory = {0:d} M \n request_virtualmemory = {0:d} M".format(
            mem
        )
        if ncpu is not None:
            batch_options += " \n request_cpus = {:d}".format(ncpu)
        if mail_user is not None:
            batch_options += " \n notify_user = {}".format(mail_user)
        if queue is not None:
            batch_options += " \n Requirements = ({}=True)".format(queue)
    else:
        raise ValueError(
            "Unrecognized batch system {}; must be one of: "
            "pbs, slurm".format(batch_system)
        )
    return batch_options


def _determine_stride_partitioning(
    obsids,
    action,
    stride_length=None,
    n_time_neighbors=None,
    time_centered=None,
    collect_stragglers=None,
):
    """
    Parameters
    ----------
    obsids : list of str
        The list of obsids.
    action : str
        The current action.
    stride_length : int, optional
        Length of the stride. Default is 1.
    n_time_neighbors : int, optional
        Number of time neighbors. Required if `stride_length` is specified.
        Otherwise optional, and default is 0.
    time_centered : bool, optional
        Whether to center the obsid and select n_time_neighbors on either side,
        returning a total of 2 * n_time_neighbors + 1 obsids (True, default), or
        a group starting with the selected obsid and a total of length
        n_time_neighbors + 1 (False).
    collect_stragglers : bool, optional
        When the list of files to work on is not divided evenly by the
        combination of stride_length and n_time_neighbors, this option specifies
        whether to include the straggler files into the last group (True) or
        treat them as their own small group (False, default).

    Returns
    -------
    primary_obsids : list of str
        A list of obsids that consist of the "primary" obsids for the current
        action, given the quantities specified. This list contains all obsids
        that will "do work" this action, in the sense that they will run a "do"
        script.
    per_obsid_primary_obsids : list of list of str
        A list of length `len(obsids)` that contains a list of "primary obsids"
        for each entry. It is assumed that these primary obsids must be
        completed for the current action before running the next action in the
        workflow. An obsid may have itself as a primary obsid (e.g., if
        stride_length == 1, then each obsid will have itself, as well as its
        time neighbors, as primary obsids). If `stride_length` and
        `n_time_neighbors` are such that there are obsids that do not belong to
        any group, then the value is an empty list.
    """
    if stride_length is not None and n_time_neighbors is None:
        raise ValueError(
            f"`stride_length` was specified for action {action}, but "
            "n_time_neighbors was not. When specifying stride_length "
            "for an action, n_time_neighbors must also be specified."
        )
    if stride_length is None:
        stride_length = 1
    if n_time_neighbors is None:
        n_time_neighbors = 0
    if time_centered is None:
        time_centered = True
    if collect_stragglers is None:
        collect_stragglers = False

    try:
        n_time_neighbors = int(n_time_neighbors)
    except ValueError:
        raise ValueError("n_time_neighbors must be able to be interpreted as an int.")
    try:
        stride_length = int(stride_length)
    except ValueError:
        raise ValueError("stride_length must be able to be interpreted as an int.")
    if type(time_centered) is not bool:
        raise ValueError(
            "time_centered must be a boolean variable. When written into the "
            "config file, do *not* use quotation marks."
        )
    if type(collect_stragglers) is not bool:
        raise ValueError(
            "collect_stragglers must be a boolean variable. When written into "
            "the config file, do *not* use quotation marks."
        )

    primary_obsids = []
    per_obsid_primary_obsids = [[] for i in range(len(obsids))]

    for idx in range(time_centered * n_time_neighbors, len(obsids), stride_length):
        # Compute the number of remaining obsids to process.
        # We account for the location of the next stride to determine if we
        # should grab straggling obsids.
        n_following = len(obsids) - (idx + stride_length)
        if time_centered:
            i1 = max(idx - n_time_neighbors, 0)
        else:
            i1 = idx
        i2 = idx + n_time_neighbors + 1
        # Check to see if i2 would be past the end of the array. If
        # `collect_stragglers` is True, then we would have broken out of the
        # loop on the iteration previous to the current one. Otherwise we drop
        # the remaining obsids because there are insufficient time neighbors to
        # make a full set.
        if i2 > len(obsids):
            break
        if n_following < (n_time_neighbors + 1) and collect_stragglers:
            # Figure out if any observations that would normally have been skipped
            # will be lumped in by getting all remaining observations.
            # "stride_length - 1" is the actual number of observations between
            # current idx and next one given stride_length.
            gap = (stride_length - 1) - n_time_neighbors * (1 + time_centered)
            if gap > 0:
                warnings.warn(
                    "Collecting stragglers is incompatible with gaps between "
                    "consecutive strides. Not collecting stragglers..."
                )
            else:
                i2 = len(obsids)
            primary_obsids.append(obsids[idx])
            for i in range(i1, i2):
                per_obsid_primary_obsids[i].append(obsids[idx])

            # skip what would have been the last iteration, because we've
            # collected the remaining obsids
            break
        # assign indices
        primary_obsids.append(obsids[idx])
        for i in range(i1, i2):
            per_obsid_primary_obsids[i].append(obsids[idx])

    return primary_obsids, per_obsid_primary_obsids


def prep_args(
    args,
    obsid,
    obsids=None,
    n_time_neighbors="1",
    stride_length="1",
    centered=None,
    collect_stragglers=None,
):
    """
    Substitute mini-language in a filename/obsid.

    Parameters
    ----------
    args : str
        String containing the arguments where mini-language is
        to be substituted.
    obsid : str
        Filename/obsid to be substituted.
    obsids : list of str, optional
        Full list of obsids. Required when time-adjacent neighbors are desired.
    n_time_neighbors : str
        Number of neighboring time files to append to list. If set to the
        string "all", then all neighbors from that JD are added.
    stride_length : str
        Number of files to include in a stride. This interacts with
        `n_time_neighbors` to define how arguments are generate.
    centered : bool, optional
        Whether the provided obsid should be in the center of the neighbors.
        If True (default), returns n_time_neighbors on either side of obsid.
        If False, returns original obsid _and_ n_time_neighbors following.
    collect_stragglers : bool, optional
        Whether to lump files close to the end of the list ("stragglers") into
        the previous group, or belong to their own smaller group.

    Returns
    -------
    output : str
        `args` string with mini-language substitutions.

    """
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

    if re.search(r"\{obsid_list\}", args):
        if centered is None:
            centered = True
        try:
            n_time_neighbors = int(n_time_neighbors)
        except ValueError:
            raise ValueError(
                "n_time_neighbors must be able to be interpreted as an int."
            )
        try:
            stride_length = int(stride_length)
        except ValueError:
            raise ValueError("stride_length must be able to be interpreted as an int.")
        obsids = sort_obsids(obsids)
        obs_idx = obsids.index(obsid)
        # Compute the number of remaining obsids to process.
        # We account for the location of the next stride to determine if we
        # should grab straggling obsids.
        n_following = len(obsids) - (obs_idx + stride_length)
        if centered:
            i1 = max(obs_idx - n_time_neighbors, 0)
        else:
            i1 = obs_idx
        i2 = min(obs_idx + n_time_neighbors + 1, len(obsids))
        if n_following < (n_time_neighbors + 1) and collect_stragglers:
            i2 = len(obsids)
        print("i1, i2: ", i1, i2)
        print("n_following: ", n_following)
        file_list = " ".join(obsids[i1:i2])
        args = re.sub(r"\{obsid_list\}", file_list, args)

    return args


def build_makeflow_from_config(
    obsids, config_file, mf_name=None, work_dir=None, **kwargs
):
    """Construct a makeflow from a config file.

    Parameters
    ----------
    obsids : list of str
        List of paths to obsids/filenames for processing.
    config_file : str
        Full path to configuration file.
    mf_name : str
        The name of the makeflow file. Defaults to "<config_file_basename>.mf"
        if not specified.
    work_dir : str
        The full path to the "work directory" where all of the wrapper scripts
        and log files will be made. Defaults to the current directory.

    Returns
    -------
    None


    Raises
    ------
    ValueError
        Raised if the config file cannot be read, or if "makeflow_type" in the
        config file is not a valid choice ("analysis" or "lstbin").

    Notes
    -----
    This function will read the "makeflow_type" entry under the "[Options]"
    header to determine if the config file specifies an "analysis" type or
    "lstbin" type, and call the appropriate funciton below.

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
    """Construct a makeflow file from a config file.

    Parameters
    ----------
    obsids : list of str
        A list of paths to obsids/filenames for processing.
    config_file : str
        The full path to configuration file.
    mf_name : str
        The name of makeflow file. Defaults to "<config_file_basename>.mf" if not
        specified.
    work_dir : str
        The full path to the "work directory" where all of the wrapper scripts and log
        files will be made. Defaults to the current directory.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        This is raised if the SETUP entry in the workflow is specified, but is
        not the first entry. Similarly, it is raised if the TEARDOWN is in the
        workflow, but not the last entry. It is also raised if a prereq for a
        step is specified that is not in the workflow.

    Notes
    -----
    Config file structure:

    [STAGENAME]
    prereqs = STAGENAME1, STAGENAME2
    args = arg1, arg2
    ncpu = 1
    mem = 5000 (MB)


    Mini-language for replacement (example):
    "{basename}" = "zen.2458000.12345.uv"

    "{prev_basename}" and "{next_basename}" are previous and subsequent files
    adjacent to "{basename}", useful for specifying prereqs

    """
    # make a cache dictionary
    _cache_dict = {}

    # load config file
    config = toml.load(config_file)
    workflow = get_config_entry(config, "WorkFlow", "actions")
    # make workflow options uppercase
    workflow = [w.upper() for w in workflow]

    # get general options
    mandc_report = get_config_entry(config, "Options", "mandc_report", required=False)

    # make sure that SETUP and TEARDOWN are in the right spots, if they are in the workflow
    try:
        idx = workflow.index("SETUP")
    except ValueError:
        pass
    else:
        if idx != 0:
            raise ValueError("SETUP must be first entry of workflow")
    try:
        idx = workflow.index("TEARDOWN")
    except ValueError:
        pass
    else:
        if idx != len(workflow) - 1:
            raise ValueError("TEARDOWN must be last entry of workflow")

    # Check for actions that use striding, make sure basename is last arg
    for action in workflow:
        stride_length = get_config_entry(
            config, action, "stride_length", required=False, total_length=len(obsids)
        )
        if stride_length is not None:
            n_time_neighbors = get_config_entry(
                config, action, "n_time_neighbors", required=False,
                total_length=len(obsids)
            )
            if n_time_neighbors is None:
                raise ValueError(
                    f"`stride_length` was specified for action {action}, but "
                    "n_time_neighbors was not. When specifying stride_length "
                    "for an action, n_time_neighbors must also be specified."
                )
            this_args = get_config_entry(config, action, "args", required=True)
            if "{obsid_list}" in this_args:
                bn_idx = this_args.index("{obsid_list}")
                if bn_idx != len(this_args) - 1:
                    raise ValueError(
                        "{obsid_list} must be the last argument for action"
                        f" {action} because stride_length is specified."
                    )

    path_to_do_scripts = get_config_entry(config, "Options", "path_to_do_scripts")
    conda_env = get_config_entry(config, "Options", "conda_env", required=False)
    source_script = get_config_entry(config, "Options", "source_script", required=False)
    mail_user = get_config_entry(config, "Options", "mail_user", required=False)
    batch_system = get_config_entry(config, "Options", "batch_system", required=False)
    timeout = get_config_entry(config, "Options", "timeout", required=False)
    if timeout is not None:
        # check that the `timeout' command exists on the system
        try:
            subprocess.check_output(["timeout", "--help"])
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
        work_dir = os.getcwd()  # pragma: no cover
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
        default_queue = get_config_entry(
            config, "Options", "default_queue", required=False
        )
        if default_queue is None:
            default_queue = "hera"

        # if we have a setup step, add it here
        if "SETUP" in workflow:
            # set parent_dir to correspond to the directory of the first obsid
            abspath = os.path.abspath(obsids[0])
            parent_dir = os.path.dirname(abspath)
            filename = os.path.basename(abspath)

            infiles = []
            command = "do_SETUP.sh"
            command = os.path.join(path_to_do_scripts, command)
            infiles.append(command)
            args = get_config_entry(config, "SETUP", "args", required=False)
            if args is not None:
                if not isinstance(args, list):
                    args = [args]
                args = " ".join(list(map(str, args)))
            else:
                args = ""
            outfile = "setup.out"
            mem = get_config_entry(config, "SETUP", "mem", required=False)
            ncpu = get_config_entry(config, "SETUP", "ncpu", required=False)
            queue = get_config_entry(config, "SETUP", "queue", required=False)
            if queue is None:
                queue = default_queue
            if mem is None:
                mem = base_mem
            if ncpu is None:
                if base_cpu is not None:
                    ncpu = base_cpu
            batch_options = process_batch_options(
                mem, ncpu, mail_user, queue, batch_system
            )
            print("export BATCH_OPTIONS = {}".format(batch_options), file=f)

            # define the logfile
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
                    print("timeout {0} {1} {2}".format(timeout, command, args), file=f2)
                else:
                    print("{0} {1}".format(command, args), file=f2)
                print("if [ $? -eq 0 ]; then", file=f2)
                print("  cd {}".format(work_dir), file=f2)
                print("  touch {}".format(outfile), file=f2)
                print("else", file=f2)
                print("  mv {0} {1}".format(logfile, logfile + ".error"), file=f2)
                print("fi", file=f2)
                print("date", file=f2)
            # make file executable
            os.chmod(wrapper_script, 0o755)

            # first line lists target file to make (dummy output file), and requirements
            # second line is "build rule", which runs the shell script and makes the output file
            infiles = " ".join(infiles)
            line1 = "{0}: {1}".format(outfile, infiles)
            line2 = "\t{0} > {1} 2>&1\n".format(wrapper_script, logfile)
            print(line1, file=f)
            print(line2, file=f)

            # save outfile as prereq for first step
            setup_outfiles = [outfile]

        # main loop over actual data files
        sorted_obsids = sort_obsids(obsids, return_basenames=False)
        for obsind, obsid in enumerate(sorted_obsids):
            # get parent directory
            abspath = os.path.abspath(obsid)
            parent_dir = os.path.dirname(abspath)
            filename = os.path.basename(abspath)

            # loop over actions for this obsid
            for ia, action in enumerate(workflow):
                if action == "SETUP":
                    outfiles_prev = setup_outfiles
                    continue
                if action == "TEARDOWN":
                    continue
                stride_length = get_config_entry(
                    config, action, "stride_length", required=False,
                    total_length=len(obsids)
                )
                n_time_neighbors = get_config_entry(
                    config, action, "n_time_neighbors", required=False,
                    total_length=len(obsids)
                )
                time_centered = get_config_entry(
                    config, action, "time_centered", required=False
                )
                collect_stragglers = get_config_entry(
                    config, action, "collect_stragglers", required=False
                )

                if n_time_neighbors is not None:
                    key1 = action + "_primary_obsids"
                    key2 = action + "_per_obsid_primary_obsids"
                    if key1 not in _cache_dict.keys():
                        (
                            primary_obsids,
                            per_obsid_primary_obsids,
                        ) = _determine_stride_partitioning(
                            sorted_obsids,
                            action,
                            stride_length=stride_length,
                            n_time_neighbors=n_time_neighbors,
                            time_centered=time_centered,
                            collect_stragglers=collect_stragglers,
                        )
                        _cache_dict[key1] = primary_obsids
                        _cache_dict[key2] = per_obsid_primary_obsids
                    else:
                        # fetch items from cache dict
                        primary_obsids = _cache_dict[key1]
                        per_obsid_primary_obsids = _cache_dict[key2]

                    if obsid not in primary_obsids:
                        # add obsid's primary obsids to list of previous
                        # outfiles and continue
                        outfiles_prev = []
                        for oi_list in per_obsid_primary_obsids:
                            for oi in oi_list:
                                outfiles_prev.extend(
                                    make_outfile_name(oi, action)
                                )
                        outfiles_prev = list(set(outfiles_prev))

                        continue

                # start list of input files
                infiles = []

                # add command to infile list
                # this implicitly checks that do_{STAGENAME}.sh script exists
                command = "do_{}.sh".format(action)
                command = os.path.join(path_to_do_scripts, command)
                infiles.append(command)

                # also add previous outfiles to input requirements
                if ia > 0:
                    for of in outfiles_prev:
                        infiles.append(of)

                # make argument list
                args = get_config_entry(config, action, "args", required=False)
                if not isinstance(args, list):
                    args = [args]
                args = " ".join(list(map(str, args)))

                # make outfile name
                outfiles = make_outfile_name(filename, action)

                # get processing options
                mem = get_config_entry(config, action, "mem", required=False)
                ncpu = get_config_entry(config, action, "ncpu", required=False)
                queue = get_config_entry(config, action, "queue", required=False)
                if mem is None:
                    mem = base_mem
                if ncpu is None:
                    if base_cpu is not None:
                        ncpu = base_cpu
                if queue is None:
                    queue = default_queue
                batch_options = process_batch_options(
                    mem, ncpu, mail_user, queue, batch_system
                )
                print("export BATCH_OPTIONS = {}".format(batch_options), file=f)

                # make rules
                for outfile in outfiles:
                    prereqs = get_config_entry(
                        config, action, "prereqs", required=False
                    )
                    if prereqs is not None:
                        if not isinstance(prereqs, list):
                            prereqs = [prereqs]
                        # get how many neighbors we should be including
                        n_time_neighbors = get_config_entry(
                            config, action, "n_time_neighbors", required=True,
                            total_length=len(obsids)
                        )
                        time_centered = get_config_entry(
                            config, action, "time_centered", required=False
                        )

                        for tp in prereqs:
                            try:
                                workflow.index(tp)
                            except ValueError:
                                raise ValueError(
                                    "Prereq {0} for action {1} not found in main "
                                    "workflow".format(tp, action)
                                )
                            # add neighbors
                            tp_outfiles = make_time_neighbor_outfile_name(
                                filename,
                                tp,
                                obsids,
                                n_time_neighbors,
                                centered=time_centered,
                            )
                            for of in tp_outfiles:
                                infiles.append(of)

                    # handle striding options
                    if stride_length is not None:
                        n_time_neighbors = get_config_entry(
                            config, action, "n_time_neighbors", required=False,
                            total_length=len(obsids)
                        )
                        centered = get_config_entry(
                            config, action, "time_centered", required=False
                        )
                        collect_stragglers = get_config_entry(
                            config, action, "collect_stragglers", required=False
                        )
                    else:
                        n_time_neighbors = None
                        centered = None
                        collect_stragglers = None

                    # replace '{basename}' with actual filename
                    prepped_args = prep_args(
                        args,
                        filename,
                        obsids=obsids,
                        n_time_neighbors=n_time_neighbors,
                        centered=centered,
                        collect_stragglers=collect_stragglers,
                    )

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
                        if mandc_report:
                            print(
                                "add_rtp_process_event.py {} started".format(filename),
                                file=f2,
                            )
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
                        if mandc_report:
                            print(
                                "  add_rtp_process_event.py {} finished".format(
                                    filename
                                ),
                                file=f2,
                            )
                        print("  cd {}".format(work_dir), file=f2)
                        print("  touch {}".format(outfile), file=f2)
                        print("else", file=f2)
                        if mandc_report:
                            print(
                                "  add_rtp_process_event.py {} error".format(filename),
                                file=f2,
                            )
                        print(
                            "  mv {0} {1}".format(logfile, logfile + ".error"), file=f2
                        )
                        print("fi", file=f2)
                        print("date", file=f2)
                    # make file executable
                    os.chmod(wrapper_script, 0o755)

                    # first line lists target file to make (dummy output file), and requirements
                    # second line is "build rule", which runs the shell script and makes the output file
                    infiles = " ".join(infiles)
                    line1 = "{0}: {1}".format(outfile, infiles)
                    line2 = "\t{0} > {1} 2>&1\n".format(wrapper_script, logfile)
                    print(line1, file=f)
                    print(line2, file=f)

                # save previous outfiles for next time
                outfiles_prev = outfiles

        # if we have a teardown step, add it here
        if "TEARDOWN" in workflow:
            # set parent_dir to correspond to the directory of the last obsid
            abspath = os.path.abspath(obsids[-1])
            parent_dir = os.path.dirname(abspath)
            filename = os.path.basename(abspath)

            # assume that we wait for all other steps of the pipeline to finish
            infiles = []
            command = "do_TEARDOWN.sh"
            command = os.path.join(path_to_do_scripts, command)
            infiles.append(command)

            # add the final outfiles for the last per-file step for all obsids
            prereq = workflow[-2]
            for obsid in obsids:
                abspath = os.path.abspath(obsid)
                parent_dir = os.path.dirname(abspath)
                filename = os.path.basename(abspath)
                outfiles = make_outfile_name(filename, prereq)
                for of in outfiles:
                    infiles.append(of)

            args = get_config_entry(config, "TEARDOWN", "args", required=False)
            if args is not None:
                if not isinstance(args, list):
                    args = [args]
                args = " ".join(list(map(str, args)))
            else:
                args = ""
            outfile = "teardown.out"
            mem = get_config_entry(config, "TEARDOWN", "mem", required=False)
            ncpu = get_config_entry(config, "TEARDOWN", "ncpu", required=False)
            queue = get_config_entry(config, "TEARDOWN", "queue", required=False)
            if mem is None:
                mem = base_mem
            if ncpu is None:
                if base_cpu is not None:
                    ncpu = base_cpu
            if queue is None:
                queue = default_queue
            batch_options = process_batch_options(
                mem, ncpu, mail_user, queue, batch_system
            )
            print("export BATCH_OPTIONS = {}".format(batch_options), file=f)

            # define the logfile
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
                        "timeout {0} {1} {2}".format(timeout, command, prepped_args),
                        file=f2,
                    )
                else:
                    print("{0} {1}".format(command, prepped_args), file=f2)
                print("if [ $? -eq 0 ]; then", file=f2)
                print("  cd {}".format(work_dir), file=f2)
                print("  touch {}".format(outfile), file=f2)
                print("else", file=f2)
                print("  mv {0} {1}".format(logfile, logfile + ".error"), file=f2)
                print("fi", file=f2)
                print("date", file=f2)
            # make file executable
            os.chmod(wrapper_script, 0o755)

            # first line lists target file to make (dummy output file), and requirements
            # second line is "build rule", which runs the shell script and makes the output file
            infiles = " ".join(infiles)
            line1 = "{0}: {1}".format(outfile, infiles)
            line2 = "\t{0} > {1} 2>&1\n".format(wrapper_script, logfile)
            print(line1, file=f)
            print(line2, file=f)

    return


def build_lstbin_makeflow_from_config(
    config_file, mf_name=None, work_dir=None, **kwargs
):
    """Construct an LST-binning makeflow file from input data and a config_file.

    Parameters
    ----------
    config_file : str
        Full path to config file containing options.
    mf_name : str
        The name of makeflow file. Defaults to "<config_file_basename>.mf" if not
        specified.

    Returns
    -------
    None


    Notes
    -----
    The major difference between this function and the one above is the use of
    the `config_lst_bin_files` function from hera_cal, which is used to
    determine the number of output files, which are parallelized over in the
    makeflow.

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
    path_to_do_scripts = get_config_entry(config, "Options", "path_to_do_scripts")
    conda_env = get_config_entry(config, "Options", "conda_env", required=False)
    source_script = get_config_entry(config, "Options", "source_script", required=False)
    batch_system = get_config_entry(config, "Options", "batch_system", required=False)
    timeout = get_config_entry(config, "Options", "timeout", required=False)
    if timeout is not None:
        # check that the `timeout' command exists on the system
        try:
            subprocess.check_output(["timeout", "--help"])
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
        mail_user = get_config_entry(config, "Options", "mail_user", required=False)
        default_queue = get_config_entry(
            config, "Options", "default_queue", required=False
        )
        if default_queue is None:
            default_queue = "hera"
        batch_options = process_batch_options(
            base_mem, base_cpu, mail_user, default_queue, batch_system
        )
        print("export BATCH_OPTIONS = {}".format(batch_options), file=f)

        # get data files
        datafiles = get_config_entry(
            config, "LSTBIN_OPTS", "data_files", required=True
        )
        # encapsulate in double quotes
        datafiles = [
            "'{}'".format(
                '"{}"'.format(os.path.join(parent_dir, df.strip('"').strip("'")))
            )
            for df in datafiles
        ]

        # get number of output files
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
            _datafiles = [
                sorted(glob.glob(df.strip("'").strip('"'))) for df in datafiles
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
            outfile = f'lstbin_outfile_{output_file_index}.LSTBIN.out'

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
                    print("source {}".format(source_script), file=f2)
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
    """Clean up wrapper scripts from work directory.

    This script removes any files in the specified directory that begin with
    "wrapper_", which is how the scripts are named in the
    'build_makeflow_from_config' function above.  It also removes files that end
    in ".wrapper", which is how makeflow labels wrapper scripts for batch
    processing.

    Parameters
    ----------
    work_dir : str
        The full path to the work directory.

    Returns
    -------
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
    """Clean up output files from work directory.

    The pipeline process uses empty files ending in '.out' to mark task
    completion. This script removes such files, since they are unnecessary once
    the pipeline is completed.

    Parameters
    ----------
    work_dir : str
        The full path to the work directory.

    Returns
    -------
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
    """Combine logs from a makeflow run into a single file.

    This function will combine the log files from a makeflow execution into a
    single file.  It also provides the option of zipping the resulting file, to
    save space.

    Parameters
    ----------
    work_dir : str
        The full path to the work directory.
    output_fn : str
        The full path to the desired output file.
    overwrite : bool
        Controls wheter to overwrite the named `output_fn` if it exists.
    remove_original : bool
        Controls whether to remove original individual logs.
    zip_file : bool
        Controls whether to zip the resulting file.

    Returns
    -------
    None

    Raises
    ------
    IOError
        This is raised if the specified output file exists, and overwrite=False.

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
