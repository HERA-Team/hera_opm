# -*- coding: utf-8 -*-
# Copyright (c) 2020 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Tests for mf_tools.py."""
import pytest
import os
import shutil
import gzip
import toml

from . import BAD_CONFIG_PATH
from ..data import DATA_PATH
from .. import mf_tools as mt


@pytest.fixture(scope="module")
def config_options():
    """Define commonly used config options."""
    config_dict = {}
    config_dict["config_file"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp.toml"
    )
    config_dict["config_file_chunk_size"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_chunk_size.toml"
    )
    config_dict["config_file_chunk_size_all"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_chunk_size_all.toml"
    )
    config_dict["config_file_options"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_options.toml"
    )
    config_dict["config_file_nopol"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_nopol.toml"
    )
    config_dict["config_file_setup_teardown"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_setup_teardown.toml"
    )
    config_dict["bad_config_file"] = os.path.join(BAD_CONFIG_PATH, "bad_example.toml")
    config_dict["bad_setup_config_file"] = os.path.join(
        BAD_CONFIG_PATH, "bad_setup_example.toml"
    )
    config_dict["bad_teardown_config_file"] = os.path.join(
        BAD_CONFIG_PATH, "bad_teardown_example.toml"
    )
    config_dict["stride_config_file"] = os.path.join(
        DATA_PATH, "sample_config", "rtp_stride_length.toml"
    )
    config_dict["bad_stride_length_file"] = os.path.join(
        BAD_CONFIG_PATH, "bad_example_stride_length.toml"
    )
    config_dict["bad_obsid_list_file"] = os.path.join(
        BAD_CONFIG_PATH, "bad_example_obsid_list.toml"
    )
    config_dict["bad_missing_prereq_file"] = os.path.join(
        BAD_CONFIG_PATH, "bad_missing_prereq.toml"
    )
    config_dict["obsids"] = (
        "zen.2458043.40141.HH.uvh5",
        "zen.2458043.40887.HH.uvh5",
        "zen.2458043.41632.HH.uvh5",
    )
    config_dict["obsids_time_discontinuous"] = (
        "zen.2458043.40141.HH.uvh5",
        "zen.2458044.40141.HH.uvh5",
        "zen.2458045.40140.HH.uvh5",
    )
    config_dict["obsids_long_dummy_list"] = (
        "aaa",
        "aab",
        "aac",
        "aad",
        "aae",
        "aaf",
        "aag",
        "aah",
        "aai",
        "aaj",
        "aak",
        "aal",
        "aam",
        "aan",
        "aao",
        "aap",
        "aaq",
        "aar",
        "aas",
        "aat",
        "aau",
        "aav",
        "aaw",
        "aax",
        "aay",
        "aaz",
    )
    return config_dict


def test_get_jd():
    """Test getting the JD from a typical filename."""
    # send in a sample file name
    filename = "zen.2458000.12345.xx.HH.uv"
    jd = mt.get_jd(filename)
    assert jd == "2458000"
    return


def test_get_jd_no_match():
    """Test if the file does not contain the JD in a way we recognize"""
    filename = "foo.txt"
    with pytest.warns(UserWarning) as record:
        retval = mt.get_jd(filename)
    assert len(record) == 1
    message = record[0].message.args[0]
    assert message.startswith("Unable to figure out the JD associated with foo.txt")
    assert retval is None

    return


def test_get_config_entry(config_options):
    """Test getting a specific entry from a config file."""
    # retreive config
    config = toml.load(config_options["config_file"])

    # retrieve specific entry
    header = "OMNICAL"
    item = "prereqs"
    assert mt.get_config_entry(config, header, item) == "FIRSTCAL_METRICS"

    # get nonexistent, but not required, entry
    header = "OMNICAL"
    item = "blah"
    assert mt.get_config_entry(config, header, item, required=False) is None

    # raise an error for a nonexistent, required entry
    with pytest.raises(AssertionError):
        mt.get_config_entry(config, header, item)
    return


def test_get_config_entry_total_length(config_options):
    """Test setting a total_length for an entry."""
    # retreive config
    config = toml.load(config_options["config_file_chunk_size_all"])

    assert mt.get_config_entry(config, "XRFI", "stride_length", total_length=15) == "15"


def test_make_outfile_name(config_options):
    """Test making the name of an output file for a specific step."""
    # define args
    obsid = config_options["obsids"][0]
    action = "OMNICAL"
    outfiles = set(["zen.2458043.40141.HH.uvh5.OMNICAL.out"])
    assert set(mt.make_outfile_name(obsid, action)) == outfiles


def test_make_chunk_list(config_options):
    # define args
    obsid = config_options["obsids"][1]
    action = "OMNICAL"
    obsids = config_options["obsids"]
    outfiles = [obs + ".OMNICAL.out" for obs in obsids[:3]]
    assert set(
        mt.make_chunk_list(
            obsid, action, obsids=obsids, chunk_size=3, return_outfiles=True
        )
    ) == set(outfiles)

    # test asking for "all" obsids
    assert set(
        mt.make_chunk_list(
            obsid, action, obsids, chunk_size="all", return_outfiles=True
        )
    ) == set(outfiles)

    # test edge cases
    obsid = obsids[0]
    assert set(
        mt.make_chunk_list(obsid, action, obsids, chunk_size=3, return_outfiles=True)
    ) == set(outfiles[:2])
    obsid = obsids[2]
    assert set(
        mt.make_chunk_list(obsid, action, obsids, chunk_size=3, return_outfiles=True)
    ) == set(outfiles[1:])
    assert set(
        mt.make_chunk_list(
            obsid,
            action,
            obsids,
            chunk_size=3,
            time_centered=False,
            return_outfiles=True,
        )
    ) == set(outfiles[2:])

    return


def test_make_chunk_list_gap(config_options):
    # test having a gap in the chunk list
    obsid = config_options["obsids"][1]
    action = "OMNICAL"
    obsids = config_options["obsids"]
    with pytest.warns(UserWarning, match="Collecting stragglers is incompatible"):
        chunk_list = mt.make_chunk_list(
            obsid,
            action,
            obsids=obsids,
            chunk_size=2,
            stride_length=3,
            collect_stragglers=True,
        )
    assert set(chunk_list) == set(obsids[:2])

    # do it again with no gap
    chunk_list = mt.make_chunk_list(
        obsid,
        action,
        obsids=obsids,
        chunk_size=3,
        stride_length=3,
        collect_stragglers=True,
    )
    assert set(chunk_list) == set(obsids)

    return


def test_make_chunk_list_errors(config_options):
    # test not having the obsid in the supplied list
    obsid = "zen.1234567.12345.xx.HH.uvcA"
    action = "OMNICAL"
    obsids = config_options["obsids"]
    with pytest.raises(ValueError):
        mt.make_chunk_list(obsid, action, obsids)

    # test passing in nonsense for chunk_size
    with pytest.raises(ValueError):
        mt.make_chunk_list(obsids[0], action, obsids, chunk_size="blah")

    # test passing in a negative number of chunk_size
    with pytest.raises(ValueError):
        mt.make_chunk_list(obsids[0], action, obsids, chunk_size="-1")

    return


def test_prep_args(config_options):
    # test having time-adjacent keywords
    obsid = config_options["obsids"][1]
    obsids = config_options["obsids"]
    args = "{basename} {prev_basename} {next_basename}"
    output = " ".join([obsids[1], obsids[0], obsids[2]])
    assert mt.prep_args(args, obsid, obsids=obsids) == output

    # test edge cases
    obsid = config_options["obsids"][0]
    output = " ".join([obsids[0], "None", obsids[1]])
    assert mt.prep_args(args, obsid, obsids=obsids) == output

    obsid = config_options["obsids"][2]
    output = " ".join([obsids[2], obsids[1], "None"])
    assert mt.prep_args(args, obsid, obsids=obsids) == output

    return


def test_prep_args_errors(config_options):
    # define args
    obsid = config_options["obsids"][0]
    obsids = config_options["obsids_long_dummy_list"]
    args = "{basename} {prev_basename}"
    # Error if requesting time-adjacent obsids without obsids list
    with pytest.raises(ValueError, match="when requesting time-adjacent"):
        mt.prep_args(args, obsid)
    # Error if obsid is not in obsids
    with pytest.raises(ValueError, match=f"{obsid} not found in list of obsids"):
        mt.prep_args(args, obsid, obsids=obsids)

    args = "{basename} {next_basename}"
    with pytest.raises(ValueError):
        # Error if requesting time-adjacent obsids without obsids list
        mt.prep_args(args, obsid)
    with pytest.raises(ValueError):
        # Error if obsid is not in obsids
        mt.prep_args(args, obsid, obsids=obsids)

    return


def test_process_batch_options_pbs():
    # define args
    mem = 8000
    ncpu = 1
    mail_user = "youremail@example.org"
    queue = "hera"
    batch_system = "pbs"
    batch_options = mt.process_batch_options(mem, ncpu, mail_user, queue, batch_system)
    assert "-l vmem=8000M,mem=8000M" in batch_options
    assert "nodes=1:ppn=1" in batch_options
    assert "-M youremail@example.org" in batch_options
    assert "-q hera" in batch_options

    return


def test_process_batch_options_slurm():
    # define args
    mem = 8000
    ncpu = 1
    mail_user = "youremail@example.org"
    queue = "hera"
    batch_system = "slurm"
    extra_options = "--gres=gpu"
    batch_options = mt.process_batch_options(
        mem, ncpu, mail_user, queue, batch_system, extra_options
    )
    assert "--mem 8000M" in batch_options
    assert "-n 1" in batch_options
    assert "--mail-user youremail@example.org" in batch_options
    assert "-p hera" in batch_options
    assert "--gres=gpu" in batch_options

    return


def test_process_batch_options_htcondor():
    # define args
    mem = 8000
    ncpu = 1
    mail_user = "youremail@example.org"
    batch_system = "htcondor"
    batch_options = mt.process_batch_options(
        mem, ncpu, mail_user, batch_system=batch_system
    )
    assert "request_memory = 8000 M \\n " in batch_options
    assert "\\n request_cpus = 1 \\n" in batch_options
    assert "\\n notify_user = youremail@example.org" in batch_options

    return


def test_process_batch_options_error():
    # test invalid batch_system
    mem = 8000
    with pytest.raises(ValueError) as cm:
        mt.process_batch_options(mem, batch_system="foo")
    assert str(cm.value).startswith("Unrecognized batch system foo")

    return


def test_determine_stride_partitioning(config_options):
    # grab the first part of the dummy list
    input_obsids = list(config_options["obsids_long_dummy_list"][:9])
    primary_obsids, per_obsid_primary_obsids = mt._determine_stride_partitioning(
        input_obsids,
        stride_length=1,
        chunk_size=5,
        time_centered=True,
        collect_stragglers=False,
    )
    # the `primary_obsids` list will only contain elements that have a
    # sufficient number of neighbors on either side (because `time_centered` is
    # True)
    assert primary_obsids == list(input_obsids[2:-2])
    # The `per_obsid_primary_obsids` list contains which obsids are considered
    # "primary obsids" _for each entry_. The first entry in the list is not a
    # primary obsid (and so does not depend on itself), and instead only depends
    # on the 3rd element of the list. The number of entries grows and then
    # shrinks as the number of available elements on either side changes based
    # on the position in the list.
    target_list = [
        ["aac"],
        ["aac", "aad"],
        ["aac", "aad", "aae"],
        ["aac", "aad", "aae", "aaf"],
        ["aac", "aad", "aae", "aaf", "aag"],
        ["aad", "aae", "aaf", "aag"],
        ["aae", "aaf", "aag"],
        ["aaf", "aag"],
        ["aag"],
    ]
    assert len(per_obsid_primary_obsids) == len(input_obsids)
    assert per_obsid_primary_obsids == target_list

    return


def test_determine_stride_partitioning_defaults(config_options):
    input_obsids = list(config_options["obsids_long_dummy_list"][:9])
    # run without specifying anything -- defaults to stride of 1 and 1 chunk
    # size
    primary_obsids, per_obsid_primary_obsids = mt._determine_stride_partitioning(
        input_obsids, time_centered=True, collect_stragglers=False
    )
    assert primary_obsids == input_obsids
    target_list = [input_obsids[idx : idx + 1] for idx in range(len(input_obsids))]
    assert per_obsid_primary_obsids == target_list

    # run again with chunk_size = 5
    primary_obsids, per_obsid_primary_obsids = mt._determine_stride_partitioning(
        input_obsids,
        chunk_size=5,
        time_centered=True,
        collect_stragglers=False,
    )
    # the results should be the same as in test_determine_stride_partitioning
    assert primary_obsids == list(input_obsids[2:-2])
    target_list = [
        ["aac"],
        ["aac", "aad"],
        ["aac", "aad", "aae"],
        ["aac", "aad", "aae", "aaf"],
        ["aac", "aad", "aae", "aaf", "aag"],
        ["aad", "aae", "aaf", "aag"],
        ["aae", "aaf", "aag"],
        ["aaf", "aag"],
        ["aag"],
    ]
    assert len(per_obsid_primary_obsids) == len(input_obsids)
    assert per_obsid_primary_obsids == target_list

    return


def test_determine_stride_partitioning_collect_stragglers(config_options):
    input_obsids = list(config_options["obsids_long_dummy_list"])
    primary_obsids, per_obsid_primary_obsids = mt._determine_stride_partitioning(
        input_obsids,
        stride_length=4,
        chunk_size=4,
        time_centered=False,
        collect_stragglers=True,
    )
    # Because time_centered is False, we should be getting every fourth entry,
    # except for the last one because that one will be collected as a straggler.
    target_obsids = input_obsids[::4][:-1]
    assert primary_obsids == target_obsids
    target_list = [[] for _ in input_obsids]
    # For each entry, there will be a single obsid corresponding to its primary
    # obsid.
    for i, oid in enumerate(target_obsids):
        idx = i * 4
        for j in range(idx, idx + 4):
            target_list[j].append(oid)

    # clean up and add stragglers
    target_list[24].append("aau")
    target_list[25].append("aau")
    assert per_obsid_primary_obsids == target_list

    return


def test_determine_stride_partitioning_errors(config_options):
    input_obsids = list(config_options["obsids_long_dummy_list"])
    with pytest.raises(
        ValueError, match="stride_length must be able to be interpreted as an int"
    ):
        mt._determine_stride_partitioning(
            input_obsids, stride_length="foo", chunk_size=3
        )

    with pytest.raises(
        ValueError, match="chunk_size must be able to be interpreted as an int"
    ):
        mt._determine_stride_partitioning(input_obsids, chunk_size="foo")

    with pytest.raises(ValueError, match="time_centered must be a boolean variable"):
        mt._determine_stride_partitioning(
            input_obsids,
            stride_length=1,
            chunk_size=2,
            time_centered="False",
        )

    with pytest.raises(
        ValueError, match="collect_stragglers must be a boolean variable"
    ):
        mt._determine_stride_partitioning(
            input_obsids,
            stride_length=1,
            chunk_size=1,
            time_centered=False,
            collect_stragglers="True",
        )

    return


@pytest.mark.filterwarnings("ignore:Collecting stragglers")
def test_determine_stride_partitioning_noncontiguous_stragglers(config_options):
    input_obsids = list(config_options["obsids_long_dummy_list"])
    primary_obsids, per_obsid_primary_obsids = mt._determine_stride_partitioning(
        input_obsids,
        stride_length=10,
        chunk_size=2,
        time_centered=False,
        collect_stragglers=True,
    )
    # in this case, because of the gap, we have the last hanging obsid
    target_obsids = input_obsids[::10]
    assert primary_obsids == target_obsids
    # make empty list
    target_list = [[] for _ in input_obsids]
    # add non-zero entries
    for i in [0, 1]:
        target_list[i].append("aaa")
    for i in [10, 11]:
        target_list[i].append("aak")
    for i in [20, 21]:
        target_list[i].append("aau")
    assert per_obsid_primary_obsids == target_list

    return


def test_build_analysis_makeflow_from_config(config_options):
    # define args
    obsids = config_options["obsids"][:1]
    config_file = config_options["config_file"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # also make sure the wrapper scripts were made
    actions = [
        "ANT_METRICS",
        "FIRSTCAL",
        "FIRSTCAL_METRICS",
        "OMNICAL",
        "OMNICAL_METRICS",
        "OMNI_APPLY",
        "XRFI",
        "XRFI_APPLY",
    ]
    for obsid in obsids:
        for action in actions:
            wrapper_fn = "wrapper_" + obsid + "." + action + ".sh"
            wrapper_fn = os.path.join(work_dir, wrapper_fn)
            assert os.path.exists(wrapper_fn)

            # check that the wrapper scripts have the right lines in them
            with open(wrapper_fn) as infile:
                lines = infile.readlines()
            assert lines[0].strip() == "#!/bin/bash"
            assert lines[1].strip() == "source ~/.bashrc"
            assert lines[2].strip() == "conda activate hera"
            assert lines[3].strip() == "date"

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # also test providing the name of the output file
    mf_output = "output.mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(
        obsids, config_file, mf_name=outfile, work_dir=work_dir
    )

    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


def test_build_analysis_makeflow_from_config_missing_prereq(config_options):
    # define args
    obsids = config_options["obsids"][:1]
    config_file = config_options["bad_missing_prereq_file"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    with pytest.raises(ValueError, match="Prereq FIRSTCAL_METRICS for action"):
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


def test_build_analysis_makeflow_from_config_chunk_size(config_options):
    # define args
    obsids = config_options["obsids"]
    config_file = config_options["config_file_chunk_size"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)
    # also make sure the wrapper scripts were made
    actions = [
        "ANT_METRICS",
        "FIRSTCAL",
        "FIRSTCAL_METRICS",
        "OMNICAL",
        "XRFI",
        "XRFI_APPLY",
    ]
    ntime_actions = ["OMNICAL_METRICS", "OMNI_APPLY"]
    for obsid in obsids:
        for action in actions:
            wrapper_fn = "wrapper_" + obsid + "." + action + ".sh"
            wrapper_fn = os.path.join(work_dir, wrapper_fn)
            assert os.path.exists(wrapper_fn)
    # some actions will not run for edge observations because they need neighbors.
    for obsid in obsids[1:-1]:
        for action in ntime_actions:
            wrapper_fn = "wrapper_" + obsid + "." + action + ".sh"
            wrapper_fn = os.path.join(work_dir, wrapper_fn)
            assert os.path.exists(wrapper_fn)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


@pytest.mark.filterwarnings("ignore:A value for the")
def test_build_analysis_makeflow_from_config_options(config_options):
    # define args
    obsids = config_options["obsids"][:1]
    config_file = config_options["config_file_options"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # also make sure the wrapper scripts were made
    actions = [
        "ANT_METRICS",
        "FIRSTCAL",
        "FIRSTCAL_METRICS",
        "OMNICAL",
        "OMNICAL_METRICS",
        "OMNI_APPLY",
        "XRFI",
        "XRFI_APPLY",
    ]
    for obsid in obsids:
        for action in actions:
            wrapper_fn = "wrapper_" + obsid + "." + action + ".sh"
            wrapper_fn = os.path.join(work_dir, wrapper_fn)
            assert os.path.exists(wrapper_fn)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # also test providing the name of the output file
    mf_output = "output.mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(
        obsids, config_file, mf_name=outfile, work_dir=work_dir
    )

    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


def test_build_analysis_makeflow_from_config_setup_teardown(config_options):
    # define args
    obsids = config_options["obsids"][:1]
    config_file = config_options["config_file_setup_teardown"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # also make sure the wrapper scripts were made
    actions = [
        "ANT_METRICS",
        "FIRSTCAL",
        "FIRSTCAL_METRICS",
        "OMNICAL",
        "OMNICAL_METRICS",
        "OMNI_APPLY",
        "XRFI",
        "XRFI_APPLY",
    ]
    # make sure there is just a single setup and teardown scriot
    wrapper_fn_setup = os.path.join(work_dir, "wrapper_setup.sh")
    wrapper_fn_teardown = os.path.join(work_dir, "wrapper_teardown.sh")
    assert os.path.exists(wrapper_fn_setup)
    assert os.path.exists(wrapper_fn_teardown)
    for obsid in obsids:
        for action in actions:
            wrapper_fn = "wrapper_" + obsid + "." + action + ".sh"
            wrapper_fn = os.path.join(work_dir, wrapper_fn)
            print("wrapper_fn: ", wrapper_fn)
            assert os.path.exists(wrapper_fn)

            # check that the wrapper scripts have the right lines in them
            with open(wrapper_fn) as infile:
                lines = infile.readlines()
            assert lines[0].strip() == "#!/bin/bash"
            assert lines[1].strip() == "source ~/.bashrc"
            assert lines[2].strip() == "conda activate hera"
            assert lines[3].strip() == "date"

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # also test providing the name of the output file
    mf_output = "output.mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_analysis_makeflow_from_config(
        obsids, config_file, mf_name=outfile, work_dir=work_dir
    )

    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


def test_setup_teardown_errors(config_options):
    # define config to load
    config_file = config_options["bad_setup_config_file"]
    obsids = config_options["obsids"][:1]

    # test bad setup location
    with pytest.raises(ValueError):
        mt.build_analysis_makeflow_from_config(obsids, config_file)

    # test bad teardown location
    config_file = config_options["bad_teardown_config_file"]
    with pytest.raises(ValueError):
        mt.build_analysis_makeflow_from_config(obsids, config_file)

    return


def test_build_makeflow_from_config(config_options):
    # define args
    obsids = config_options["obsids"][:1]
    config_file = config_options["config_file"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # ensure we raise an error when no makeflow_type is specified
    config_file = config_options["bad_config_file"]
    with pytest.raises(ValueError):
        mt.build_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    return


def test_clean_wrapper_scripts():
    # define args
    work_dir = os.path.join(DATA_PATH, "test_output")

    # make file to remove
    outfile = os.path.join(work_dir, "wrapper_test.sh")
    if os.path.exists(outfile):
        os.remove(outfile)
    open(outfile, "a").close()

    # check that it exists
    assert os.path.exists(outfile)

    # remove it
    mt.clean_wrapper_scripts(work_dir)
    assert not os.path.exists(outfile)
    return


def test_clean_output_files():
    # define args
    work_dir = os.path.join(DATA_PATH, "test_output")

    # make file to remove
    outfile = os.path.join(work_dir, "test_file.out")
    if os.path.exists(outfile):
        os.remove(outfile)
    open(outfile, "a").close()

    # check that it exists
    assert os.path.exists(outfile)

    # remove it
    mt.clean_output_files(work_dir)
    assert not os.path.exists(outfile)
    return


def test_consolidate_logs():
    # define args
    input_dir = os.path.join(DATA_PATH, "test_input")
    work_dir = os.path.join(DATA_PATH, "test_output")
    output_fn = os.path.join(DATA_PATH, "test_output", "mf.log")

    # copy input files over to output directory
    input_files = [f for f in os.listdir(input_dir) if f[-4:] == ".log"]
    for fn in input_files:
        abspath = os.path.join(input_dir, fn)
        shutil.copy(abspath, work_dir)

    # create single log file from input logs
    if os.path.exists(output_fn):
        os.remove(output_fn)
    mt.consolidate_logs(work_dir, output_fn, remove_original=False, zip_file=False)

    # check that output file exists
    assert os.path.exists(output_fn)

    # make sure that individual logs' content was transferred over
    with open(output_fn, "r") as f_out:
        out_lines = set(f_out.read().splitlines())
        for fn in input_files:
            abspath = os.path.join(input_dir, fn)
            with open(abspath, "r") as f_in:
                # check log content
                in_lines = set(f_in.read().splitlines())
                for line in in_lines:
                    assert line in out_lines
            # also check file name
            assert fn in out_lines

    # test overwriting file
    mt.consolidate_logs(
        work_dir, output_fn, overwrite=True, remove_original=False, zip_file=False
    )

    # make sure that individual logs' content was transferred over
    with open(output_fn, "r") as f_out:
        out_lines = set(f_out.read().splitlines())
        for fn in input_files:
            abspath = os.path.join(input_dir, fn)
            with open(abspath, "r") as f_in:
                # check log content
                in_lines = set(f_in.read().splitlines())
                for line in in_lines:
                    assert line in out_lines
            # also check file name
            assert fn in out_lines

    # test making a zip
    mt.consolidate_logs(
        work_dir, output_fn, overwrite=True, remove_original=False, zip_file=True
    )

    # check that file exists
    output_gz = output_fn + ".gz"
    assert os.path.exists(output_gz)

    # make sure that individual logs' content was transferred over
    with gzip.open(output_gz, "rb") as f_out:
        data = f_out.read().decode("utf-8")
        out_lines = set(data.splitlines())
        print(out_lines)
        for fn in input_files:
            abspath = os.path.join(input_dir, fn)
            with open(abspath, "r") as f_in:
                # check log content
                in_lines = set(f_in.read().splitlines())
                for line in in_lines:
                    print(line)
                    assert line in out_lines
            # also check file name
            assert fn in out_lines

    # test overwriting a zip
    mt.consolidate_logs(
        work_dir, output_fn, overwrite=True, remove_original=False, zip_file=True
    )
    assert os.path.exists(output_gz)

    # test removing input files when a log is made
    for fn in input_files:
        abspath = os.path.join(work_dir, fn)
        assert os.path.exists(abspath)

    mt.consolidate_logs(work_dir, output_fn, overwrite=True, remove_original=True)

    # make sure that original files are now gone
    for fn in input_files:
        abspath = os.path.join(work_dir, fn)
        assert not os.path.exists(abspath)

    # clean up after ourselves
    os.remove(output_fn)
    os.remove(output_fn + ".gz")

    return


def test_consolidate_logs_errors():
    # define args
    input_dir = os.path.join(DATA_PATH, "test_input")
    work_dir = os.path.join(DATA_PATH, "test_output")
    output_fn = os.path.join(DATA_PATH, "test_output", "mf.log")

    # copy input files over to output directory
    input_files = [f for f in os.listdir(input_dir) if f[-4:] == ".log"]
    for fn in input_files:
        abspath = os.path.join(input_dir, fn)
        shutil.copy(abspath, work_dir)

    # create single log file from input logs
    if os.path.exists(output_fn):
        os.remove(output_fn)
    mt.consolidate_logs(work_dir, output_fn, remove_original=False, zip_file=False)

    # make sure that we raise an error if we don't pass overwrite=True
    with pytest.raises(IOError):
        mt.consolidate_logs(work_dir, output_fn, overwrite=False)

    # test making a zip
    mt.consolidate_logs(
        work_dir, output_fn, overwrite=True, remove_original=False, zip_file=True
    )

    # check that file exists
    output_gz = output_fn + ".gz"
    assert os.path.exists(output_gz)

    # make sure we get an error if the file exists
    with pytest.raises(IOError):
        mt.consolidate_logs(work_dir, output_fn, overwrite=False, zip_file=True)

    # clean up after ourselves
    for fn in input_files:
        abspath = os.path.join(work_dir, fn)
        os.remove(abspath)
    os.remove(output_gz)

    return


def test_interpolate_config(config_options):
    # define and load config file
    config_file = config_options["config_file"]
    config = toml.load(config_file)

    # interpolate config
    opt = mt._interpolate_config(config, "${Options:ex_ants}")
    assert opt == "~/hera/hera_cal/hera_cal/calibrations/herahex_ex_ants.txt"

    # raise error
    with pytest.raises(ValueError):
        mt._interpolate_config(config, "${Bad:interp}")

    return


def test_build_makeflow_from_config_errors():
    # try to pass in something that is not a string
    with pytest.raises(ValueError):
        mt.build_makeflow_from_config(["obids"], 3)

    return


def test_sort_obsids(config_options):
    # get obsids
    obsids = config_options["obsids"]

    # scramble them and make sure we get a sorted list back
    obsids_swap = list(obsids)
    temp = obsids_swap[1]
    obsids_swap[1] = obsids_swap[0]
    obsids_swap[0] = temp

    obsids_sort = mt.sort_obsids(obsids_swap)
    assert tuple(obsids_sort) == obsids

    # also check the "jd" option works
    obsids_discontinuous = config_options["obsids_time_discontinuous"]
    obsids_swap = list(obsids_discontinuous)
    temp = obsids_swap[1]
    obsids_swap[1] = obsids_swap[0]
    obsids_swap[0] = temp

    obsids_sort = mt.sort_obsids(obsids_swap, jd="2458044")
    assert tuple(obsids_sort) == tuple([obsids_discontinuous[1]])

    return


def test_prep_args_obsid_list(config_options):
    # define args to parse
    obsids_list = config_options["obsids"]
    args = "{obsid_list}"
    obsid = obsids_list[1]

    args = mt.prep_args(
        args,
        obsid,
        obsids=obsids_list,
        chunk_size="3",
        time_centered=None,
        collect_stragglers=False,
    )
    prepped_args = " ".join(obsids_list[0:3])
    assert args == prepped_args

    return


def test_prep_args_obsid_list_centered(config_options):
    # define args to parse
    obsids_list = config_options["obsids"]
    args = "{obsid_list}"
    obsid = obsids_list[1]

    args = mt.prep_args(
        args,
        obsid,
        obsids=obsids_list,
        chunk_size="3",
        time_centered=True,
        collect_stragglers=False,
    )
    prepped_args = " ".join(obsids_list[0:3])
    assert args == prepped_args

    return


def test_prep_args_obsid_list_not_centered(config_options):
    # define args to parse
    obsids_list = config_options["obsids"]
    args = "{obsid_list}"
    obsid = obsids_list[1]

    args = mt.prep_args(
        args,
        obsid,
        obsids=obsids_list,
        chunk_size="2",
        time_centered=False,
        collect_stragglers=False,
    )
    prepped_args = " ".join(obsids_list[1:3])
    assert args == prepped_args

    return


def test_prep_args_obsid_list_with_stragglers(config_options):
    # define args to parse
    obsids_list = config_options["obsids"]
    args = "{obsid_list}"
    obsid = obsids_list[0]

    args = mt.prep_args(
        args,
        obsid,
        obsids=obsids_list,
        chunk_size="2",
        stride_length="2",
        time_centered=False,
        collect_stragglers=True,
    )
    prepped_args = " ".join(obsids_list)
    assert args == prepped_args

    return


def test_prep_args_obsid_list_returned(config_options):
    # define args to parse
    obsids_list = config_options["obsids"]
    args = "{obsid_list}"
    obsid = obsids_list[1]

    args, obsid_list = mt.prep_args(
        args,
        obsid,
        obsids=obsids_list,
        chunk_size="3",
        time_centered=None,
        collect_stragglers=False,
        return_obsid_list=True,
    )
    prepped_args = " ".join(obsids_list[0:3])
    assert args == prepped_args
    assert obsid_list == list(obsids_list)

    return


def test_prep_args_obsid_list_error(config_options):
    # define args to parse
    obsids_list = config_options["obsids"]
    args = "{obsid_list}"
    obsid = obsids_list[1]

    with pytest.raises(ValueError) as cm:
        args = mt.prep_args(
            args,
            obsid,
            obsids=obsids_list,
            chunk_size="foo",
            time_centered=True,
            collect_stragglers=False,
        )
    assert str(cm.value).startswith("chunk_size must be able to be interpreted")

    with pytest.raises(ValueError) as cm:
        args = mt.prep_args(
            args,
            obsid,
            obsids=obsids_list,
            chunk_size="3",
            stride_length="foo",
            time_centered=True,
            collect_stragglers=False,
        )
    assert str(cm.value).startswith("stride_length must be able to be interpreted")

    return


def test_build_analysis_makeflow_error_obsid_list(config_options):
    config_file = config_options["bad_obsid_list_file"]
    obsids = config_options["obsids"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    with pytest.raises(ValueError) as cm:
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)
    assert str(cm.value).startswith("{obsid_list} must be the last argument")

    return
