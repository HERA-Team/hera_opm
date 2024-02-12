"""Tests for utils.py"""

import pytest
import hera_opm.utils as utils


def test_get_makeflow_ArgumentParser():
    # get an argument parser and make sure it behaves as expected
    a = utils.get_makeflow_ArgumentParser()
    config_file = "config_file.cfg"
    output_file = "mf.log"
    obsids = ["zen.2458000.12345.xx.uv", "zen.2458000.12345.yy.uv"]
    args = ["-c", config_file, "-o", output_file, obsids[0], obsids[1]]
    parsed_args = a.parse_args(args)

    # make sure we got what we expected
    assert parsed_args.config == config_file
    assert parsed_args.output == output_file
    for obsid in obsids:
        assert obsid in parsed_args.files
    assert parsed_args.scan_files is False
    assert parsed_args.rename_bad_files is False
    assert parsed_args.bad_suffix == ".METADATA_ERROR"

    return


def test_get_cleaner_ArgumentParser():
    # raise error for requesting unknown function
    with pytest.raises(AssertionError):
        utils.get_cleaner_ArgumentParser("blah")

    # test getting each type of argparser
    # wrapper
    a = utils.get_cleaner_ArgumentParser("wrapper")
    work_dir = "/foo/bar"
    args = [work_dir]
    parsed_args = a.parse_args(args)
    assert parsed_args.directory == work_dir

    # output
    a = utils.get_cleaner_ArgumentParser("output")
    parsed_args = a.parse_args(args)
    assert parsed_args.directory == work_dir

    # logs
    a = utils.get_cleaner_ArgumentParser("logs")
    output_file = "mf.log"
    args = [work_dir, "-o", output_file]
    parsed_args = a.parse_args(args)
    assert parsed_args.directory == work_dir
    assert parsed_args.output == output_file
    assert not parsed_args.overwrite
    assert parsed_args.remove_original
    assert not parsed_args.zip

    return
