"""Tests for mf_tools.py"""
import pytest
import os
import shutil
import gzip
import glob
from hera_opm.data import DATA_PATH
from hera_opm import mf_tools as mt
import six
import toml


# define a pytest marker for skipping lstbin tests
try:
    import hera_cal

    hc_installed = True
except ImportError:
    hc_installed = False
hc_skip = pytest.mark.skipif(
    not hc_installed, reason="hera_cal must be installed for this test"
)


@pytest.fixture(scope="module")
def config_options():
    config_dict = {}
    config_dict["config_file"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp.toml"
    )
    config_dict["config_file_time_neighbors"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_time_neighbors.toml"
    )
    config_dict["config_file_options"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_options.toml"
    )
    config_dict["config_file_nopol"] = os.path.join(
        DATA_PATH, "sample_config", "nrao_rtp_nopol.toml"
    )
    config_dict["config_file_lstbin"] = os.path.join(
        DATA_PATH, "sample_config", "lstbin.toml"
    )
    config_dict["config_file_lstbin_options"] = os.path.join(
        DATA_PATH, "sample_config", "lstbin_options.toml"
    )
    config_dict["bad_config_file"] = os.path.join(
        DATA_PATH, "sample_config", "bad_example.toml"
    )
    config_dict["obsids_pol"] = (
        "zen.2457698.40355.xx.HH.uvcA",
        "zen.2457698.40355.xy.HH.uvcA",
        "zen.2457698.40355.yx.HH.uvcA",
        "zen.2457698.40355.yy.HH.uvcA",
    )
    config_dict["obsids_nopol"] = ("zen.2457698.40355.HH.uvcA",)
    config_dict["obsids_lstbin"] = (
        sorted(glob.glob(DATA_PATH + "/zen.245804{}.*.xx.HH.uvXRAA".format(i)))
        for i in [3, 4, 5]
    )
    config_dict["pols"] = ("xx", "xy", "yx", "yy")
    config_dict["obsids_time"] = (
        "zen.2457698.30355.xx.HH.uvcA",
        "zen.2457698.40355.xx.HH.uvcA",
        "zen.2457698.50355.xx.HH.uvcA",
    )
    return config_dict


def test_get_jd():
    # send in a sample file name
    filename = "zen.2458000.12345.xx.HH.uv"
    jd = mt.get_jd(filename)
    assert jd == "2458000"
    return


def test_get_config_entry(config_options):
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
    with pytest.raises(AttributeError):
        mt.get_config_entry(config, header, item)
    return


def test_make_outfile_name(config_options):
    # define args
    obsid = config_options["obsids_pol"][0]
    action = "OMNICAL"
    pols = config_options["pols"]
    outfiles = set(
        [
            "zen.2457698.40355.xx.HH.uvcA.OMNICAL.xx.out",
            "zen.2457698.40355.xx.HH.uvcA.OMNICAL.xy.out",
            "zen.2457698.40355.xx.HH.uvcA.OMNICAL.yx.out",
            "zen.2457698.40355.xx.HH.uvcA.OMNICAL.yy.out",
        ]
    )
    assert set(mt.make_outfile_name(obsid, action, pols)) == outfiles

    # run for no polarizations
    pols = []
    outfiles = ["zen.2457698.40355.xx.HH.uvcA.OMNICAL.out"]
    assert mt.make_outfile_name(obsid, action, pols) == outfiles
    return


def test_make_time_neighbor_outfile_name(config_options):
    # define args
    obsid = config_options["obsids_time"][1]
    action = "OMNICAL"
    pol = config_options["pols"][3]
    outfiles = [
        "zen.2457698.30355.xx.HH.uvcA.OMNICAL.yy.out",
        "zen.2457698.40355.xx.HH.uvcA.OMNICAL.yy.out",
        "zen.2457698.50355.xx.HH.uvcA.OMNICAL.yy.out",
    ]
    obsids_time = config_options["obsids_time"]
    assert set(
        mt.make_time_neighbor_outfile_name(obsid, action, obsids_time, pol)
    ) == set(outfiles)

    # test asking for "all" neighbors
    assert set(
        mt.make_time_neighbor_outfile_name(
            obsid, action, obsids_time, pol, n_neighbors="all"
        )
    ) == set(outfiles)

    # test edge cases
    obsid = obsids_time[0]
    assert set(
        mt.make_time_neighbor_outfile_name(obsid, action, obsids_time, pol)
    ) == set(outfiles[:2])
    obsid = obsids_time[2]
    assert set(
        mt.make_time_neighbor_outfile_name(obsid, action, obsids_time, pol)
    ) == set(outfiles[1:])

    # run for no polarizations
    obsid = obsids_time[1]
    outfiles = set(
        [
            "zen.2457698.30355.xx.HH.uvcA.OMNICAL.out",
            "zen.2457698.40355.xx.HH.uvcA.OMNICAL.out",
            "zen.2457698.50355.xx.HH.uvcA.OMNICAL.out",
        ]
    )
    assert (
        set(mt.make_time_neighbor_outfile_name(obsid, action, obsids_time)) == outfiles
    )
    return


def test_make_time_neighbor_outfile_name_errors(config_options):
    # test not having the obsid in the supplied list
    obsid = "zen.1234567.12345.xx.HH.uvcA"
    action = "OMNICAL"
    obsids_time = config_options["obsids_time"]
    with pytest.raises(ValueError):
        mt.make_time_neighbor_outfile_name(obsid, action, obsids_time)

    # test passing in nonsense for all_neighbors
    with pytest.raises(ValueError):
        mt.make_time_neighbor_outfile_name(
            obsids_time[0], action, obsids_time, pol="xx", n_neighbors="blah"
        )

    # test passing in a negative number of neighbors
    with pytest.raises(ValueError):
        mt.make_time_neighbor_outfile_name(
            obsids_time[0], action, obsids_time, pol="xx", n_neighbors="-1"
        )

    return


def test_prep_args(config_options):
    # define args
    obsid = config_options["obsids_pol"][0]
    args = "{basename}"
    pol = config_options["pols"][3]
    output = "zen.2457698.40355.yy.HH.uvcA"
    assert mt.prep_args(args, obsid, pol) == output

    # test requesting polarization, but none found in file
    obsid = "zen.2457698.40355.uv"
    assert mt.prep_args(args, obsid, pol) == obsid

    # test not requesting polarization
    obsid = config_options["obsids_pol"][0]
    output = "zen.2457698.40355.xx.HH.uvcA"
    assert mt.prep_args(args, obsid) == output

    # test having time-adjacent keywords
    obsid = config_options["obsids_time"][1]
    obsids = config_options["obsids_time"]
    args = "{basename} {prev_basename} {next_basename}"
    output = "zen.2457698.40355.xx.HH.uvcA zen.2457698.30355.xx.HH.uvcA zen.2457698.50355.xx.HH.uvcA"
    assert mt.prep_args(args, obsid, obsids=obsids) == output

    # test edge cases
    obsid = config_options["obsids_time"][0]
    output = "zen.2457698.30355.xx.HH.uvcA None zen.2457698.40355.xx.HH.uvcA"
    assert mt.prep_args(args, obsid, obsids=obsids) == output

    obsid = config_options["obsids_time"][2]
    output = "zen.2457698.50355.xx.HH.uvcA zen.2457698.40355.xx.HH.uvcA None"
    assert mt.prep_args(args, obsid, obsids=obsids) == output

    return


def test_prep_args_errors(config_options):
    # define args
    obsid = config_options["obsids_time"][0]
    obsids = config_options["obsids_pol"]
    args = "{basename} {prev_basename}"
    with pytest.raises(ValueError):
        mt.prep_args(args, obsid)
    with pytest.raises(ValueError):
        mt.prep_args(args, obsid, obsids=obsids)

    args = "{basename} {next_basename}"
    with pytest.raises(ValueError):
        mt.prep_args(args, obsid)
    with pytest.raises(ValueError):
        mt.prep_args(args, obsid, obsids=obsids)

    return


def test_process_batch_options():
    # define args
    mem = 8000
    ncpu = 1
    pbs_mail_user = "youremail@example.org"
    queue = "hera"
    batch_options = mt.process_batch_options(mem, ncpu, pbs_mail_user, queue)
    assert "-l vmem=8000M,mem=8000M" in batch_options
    assert "nodes=1:ppn=1" in batch_options
    assert "-M youremail@example.org" in batch_options
    assert "-q hera" in batch_options
    return


def test_build_analysis_makeflow_from_config(config_options):
    # define args
    obsids = config_options["obsids_pol"][:1]
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
    pols = config_options["pols"]
    for obsid in obsids:
        for action in actions:
            for pol in pols:
                wrapper_fn = "wrapper_" + obsid + "." + action + "." + pol + ".sh"
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


def test_build_analysis_makeflow_from_config_time_neighbors(config_options):
    # define args
    obsids = config_options["obsids_time"]
    config_file = config_options["config_file_time_neighbors"]
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
    pols = config_options["pols"]
    for obsid in obsids:
        for action in actions:
            for pol in pols:
                wrapper_fn = "wrapper_" + obsid + "." + action + "." + pol + ".sh"
                wrapper_fn = os.path.join(work_dir, wrapper_fn)
                assert os.path.exists(wrapper_fn)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


def test_build_analysis_makeflow_from_config_errors(config_options):
    # define args
    obsids = config_options["obsids_pol"][:2]
    config_file = config_options["config_file"]
    work_dir = os.path.join(DATA_PATH, "test_output")

    # raise an error for passing in obsids with different polarizations
    with pytest.raises(AssertionError):
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    # raise an error for passing in an obsid with no polarization string
    obsids = ["zen.2458000.12345.uv"]
    with pytest.raises(AssertionError):
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

    return


def test_build_analysis_makeflow_from_config_options(config_options):
    # define args
    obsids = config_options["obsids_pol"][:1]
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
    pols = config_options["pols"]
    for obsid in obsids:
        for action in actions:
            for pol in pols:
                wrapper_fn = "wrapper_" + obsid + "." + action + "." + pol + ".sh"
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


def test_build_analysis_makeflow_from_config_nopol(config_options):
    # define args
    obsids = config_options["obsids_nopol"]
    config_file = config_options["config_file_nopol"]
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
            print("obsid, action: ", obsid, action)
            print("work_dir: ", work_dir)
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


@hc_skip
@pytest.mark.filterwarnings("ignore:The default for the `center` keyword has changed")
def test_build_lstbin_makeflow_from_config(config_options):
    # define load in config
    config_file = config_options["config_file_lstbin"]

    # setup vars
    work_dir = os.path.join(DATA_PATH, "test_output")
    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_lstbin_makeflow_from_config(
        config_file, mf_name="lstbin.mf", work_dir=work_dir, parent_dir=DATA_PATH
    )

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # also test providing the name of the output file
    mf_output = "output.mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_lstbin_makeflow_from_config(
        config_file, mf_name=outfile, work_dir=work_dir, parent_dir=DATA_PATH
    )

    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # test v2 LSTBIN pipe with no pols provided
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_lstbin_makeflow_from_config(config_file.replace("lstbin", "lstbin_v2"), mf_name="lstbin.mf",
        work_dir=work_dir, parent_dir=DATA_PATH
    )

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


@hc_skip
@pytest.mark.filterwarnings("ignore:The default for the `center` keyword has changed")
def test_build_lstbin_makeflow_from_config_options(config_options):
    # define load in config
    config_file = config_options["config_file_lstbin_options"]

    # setup vars
    work_dir = os.path.join(DATA_PATH, "test_output")
    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_lstbin_makeflow_from_config(
        config_file, mf_name=outfile, work_dir=work_dir, parent_dir=DATA_PATH
    )

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    # also test providing the name of the output file
    mf_output = "output.mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)
    mt.build_lstbin_makeflow_from_config(
        config_file, mf_name=outfile, work_dir=work_dir, parent_dir=DATA_PATH
    )

    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

    return


def test_build_makeflow_from_config(config_options):
    # define args
    obsids = config_options["obsids_pol"][:1]
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


@hc_skip
@pytest.mark.filterwarnings("ignore:The default for the `center` keyword has changed")
def test_build_makeflow_from_config_lstbin_options(config_options):
    # test lstbin version with options
    obsids = config_options["obsids_pol"][:1]
    config_file = config_options["config_file_lstbin_options"]
    work_dir = os.path.join(DATA_PATH, "test_output")
    mf_output = os.path.splitext(os.path.basename(config_file))[0] + ".mf"
    outfile = os.path.join(work_dir, mf_output)
    if os.path.exists(outfile):
        os.remove(outfile)

    mt.build_makeflow_from_config(
        obsids, config_file, mf_name=outfile, work_dir=work_dir, parent_dir=DATA_PATH
    )

    # make sure the output files we expected appeared
    assert os.path.exists(outfile)

    # clean up after ourselves
    os.remove(outfile)
    mt.clean_wrapper_scripts(work_dir)

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
        data = f_out.read()
        if six.PY3:
            data = data.decode("utf-8")
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
