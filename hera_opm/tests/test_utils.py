"""Tests for utils.py"""
import nose.tools as nt
import os
from hera_opm.data import DATA_PATH
import hera_opm.utils as utils

def test_get_makeflow_ArgumentParser():
    # get an argument parser and make sure it behaves as expected
    a = utils.get_makeflow_ArgumentParser()
    config_file = "config_file.cfg"
    output_file = "mf.log"
    obsids = ['zen.2458000.12345.xx.uv', 'zen.2458000.12345.yy.uv']
    args = ['-c', config_file, '-o', output_file, obsids[0], obsids[1]]
    parsed_args = a.parse_args(args)

    # make sure we got what we expected
    nt.assert_equal(parsed_args.config, config_file)
    nt.assert_equal(parsed_args.output, output_file)
    for obsid in obsids:
        nt.assert_true(obsid in parsed_args.files)

    return


def test_get_cleaner_ArgumentParser():
    # raise error for requesting unknown function
    nt.assert_raises(AssertionError, utils.get_cleaner_ArgumentParser, 'blah')

    # test getting each type of argparser
    # wrapper
    a = utils.get_cleaner_ArgumentParser('wrapper')
    work_dir = '/foo/bar'
    args = [work_dir]
    parsed_args = a.parse_args(args)
    nt.assert_equal(work_dir, parsed_args.directory)

    # output
    a = utils.get_cleaner_ArgumentParser('output')
    parsed_args = a.parse_args(args)
    nt.assert_equal(work_dir, parsed_args.directory)

    # logs
    a = utils.get_cleaner_ArgumentParser('logs')
    output_file = "mf.log"
    args = [work_dir, '-o', output_file]
    parsed_args = a.parse_args(args)
    nt.assert_equal(work_dir, parsed_args.directory)
    nt.assert_equal(output_file, parsed_args.output)
    nt.assert_false(parsed_args.overwrite)
    nt.assert_true(parsed_args.remove_original)
    nt.assert_false(parsed_args.zip)

    return
