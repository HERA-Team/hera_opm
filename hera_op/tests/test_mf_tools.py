"""Tests for mf_tools.py"""

import nose.tools as nt
import os
import shutil
import gzip
from hera_op.data import DATA_PATH
import hera_op.mf_tools as mt
import ConfigParser as configparser
from configparser import ConfigParser, ExtendedInterpolation

class TestMethods(object):
    def setUp(self):
        self.config_file = os.path.join(DATA_PATH, 'sample_config', 'nrao_rtp.cfg')
        self.obsids_pol = ['zen.2457698.40355.xx.HH.uvcA', 'zen.2457698.40355.xy.HH.uvcA',
                           'zen.2457698.40355.yx.HH.uvcA', 'zen.2457698.40355.yy.HH.uvcA']
        self.obsids_nopol = ['zen.2457698.40355.HH.uvcA']
        self.pols = ['xx', 'xy', 'yx', 'yy']
        return

    def test_get_config_entry(self):
        # retreive config
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(self.config_file)

        # retrieve specific entry
        header = 'OMNICAL'
        item = 'prereqs'
        nt.assert_equal(["FIRSTCAL_METRICS"], mt.get_config_entry(config, header, item))

        # get nonexistent, but not required, entry
        header = 'OMNICAL'
        item = 'blah'
        nt.assert_equal([], mt.get_config_entry(config, header, item, required=False))

        # raise an error for a nonexistent, required entry
        nt.assert_raises(AttributeError, mt.get_config_entry, config, header, item)
        return

    def test_make_outfile_name(self):
        # define args
        obsid = self.obsids_pol[0]
        action = 'OMNICAL'
        pols = self.pols
        outfiles = set(['zen.2457698.40355.xx.HH.uvcA.OMNICAL.xx.out', 'zen.2457698.40355.xx.HH.uvcA.OMNICAL.xy.out',
                        'zen.2457698.40355.xx.HH.uvcA.OMNICAL.yx.out', 'zen.2457698.40355.xx.HH.uvcA.OMNICAL.yy.out'])
        nt.assert_equal(outfiles, set(mt.make_outfile_name(obsid, action, pols)))

        # run for no polarizations
        pols = []
        outfiles = ['zen.2457698.40355.xx.HH.uvcA.OMNICAL.out']
        nt.assert_equal(outfiles, mt.make_outfile_name(obsid, action, pols))
        return

    def test_prep_args(self):
        # define args
        obsid = self.obsids_pol[0]
        args = '{basename}'
        pol = self.pols[3]
        output = 'zen.2457698.40355.yy.uvcA'
        nt.assert_equal(output, mt.prep_args(args, obsid, pol))
        return

    def test_build_makeflow_from_config(self):
        # define args
        obsids = self.obsids_pol
        config_file = self.config_file
        mf_name = "test"
        work_dir = os.path.join(DATA_PATH, 'test_output')

        mf_output = mf_name + '.' + os.path.basename(config_file) + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_makeflow_from_config(obsids, config_file, mf_name, work_dir)

        # make sure the output files we expected appeared
        nt.assert_true(os.path.exists(outfile))

        # also make sure the wrapper scripts were made
        actions = ['ANT_METRICS', 'FIRSTCAL', 'FIRSTCAL_METRICS', 'OMNICAL', 'OMNICAL_METRICS',
                   'OMNI_APPLY', 'XRFI', 'XRFI_APPLY']
        pols = self.pols
        for obsid in obsids:
            for action in actions:
                for pol in pols:
                    wrapper_fn = 'wrapper_' + obsid + '.' + action + '.' + pol + '.sh'
                    wrapper_fn = os.path.join(work_dir, wrapper_fn)
                    nt.assert_true(os.path.exists(wrapper_fn))

        # clean up after ourselves
        mt.clean_wrapper_scripts(work_dir)
        return

    def test_clean_wrapper_scripts(self):
        # define args
        work_dir = os.path.join(DATA_PATH, 'test_output')

        # make file to remove
        outfile = os.path.join(work_dir, 'wrapper_test.sh')
        if os.path.exists(outfile):
            os.remove(outfile)
        open(outfile, 'a').close()

        # check that it exists
        nt.assert_true(os.path.exists(outfile))

        # remove it
        mt.clean_wrapper_scripts(work_dir)
        nt.assert_false(os.path.exists(outfile))
        return

    def test_clean_output_files(self):
        # define args
        work_dir = os.path.join(DATA_PATH, 'test_output')

        # make file to remove
        outfile = os.path.join(work_dir, 'test_file.out')
        if os.path.exists(outfile):
            os.remove(outfile)
        open(outfile, 'a').close()

        # check that it exists
        nt.assert_true(os.path.exists(outfile))

        # remove it
        mt.clean_output_files(work_dir)
        nt.assert_false(os.path.exists(outfile))
        return

    def test_consolidate_logs(self):
        # define args
        input_dir = os.path.join(DATA_PATH, 'test_input')
        work_dir = os.path.join(DATA_PATH, 'test_output')
        output_fn = os.path.join(DATA_PATH, 'test_output', 'mf.log')

        # copy input files over to output directory
        input_files = [f for f in os.listdir(input_dir) if f[-4:] == '.log']
        for fn in input_files:
            abspath = os.path.join(input_dir, fn)
            shutil.copy(abspath, work_dir)

        # create single log file from input logs
        if os.path.exists(output_fn):
            os.remove(output_fn)
        mt.consolidate_logs(work_dir, output_fn, remove_original=False, zip_file=False)

        # check that output file exists
        nt.assert_true(os.path.exists(output_fn))

        # make sure that individual logs' content was transferred over
        with open(output_fn, 'r') as f_out:
            out_lines = set(f_out.read().splitlines())
            for fn in input_files:
                abspath = os.path.join(input_dir, fn)
                with open(abspath, 'r') as f_in:
                    # check log content
                    in_lines = set(f_in.read().splitlines())
                    for line in in_lines:
                        nt.assert_true(line in out_lines)
                # also check file name
                nt.assert_true(fn in out_lines)

        # test overwriting file
        mt.consolidate_logs(work_dir, output_fn, overwrite=True, remove_original=False,
                            zip_file=False)

        # make sure that individual logs' content was transferred over
        with open(output_fn, 'r') as f_out:
            out_lines = set(f_out.read().splitlines())
            for fn in input_files:
                abspath = os.path.join(input_dir, fn)
                with open(abspath, 'r') as f_in:
                    # check log content
                    in_lines = set(f_in.read().splitlines())
                    for line in in_lines:
                        nt.assert_true(line in out_lines)
                # also check file name
                nt.assert_true(fn in out_lines)

        # test making a zip
        mt.consolidate_logs(work_dir, output_fn, overwrite=True, remove_original=False,
                            zip_file=True)

        # check that file exists
        output_gz = output_fn + '.gz'
        nt.assert_true(os.path.exists(output_gz))

        # make sure that individual logs' content was transferred over
        with gzip.open(output_gz, 'r') as f_out:
            out_lines = set(f_out.read().splitlines())
            for fn in input_files:
                abspath = os.path.join(input_dir, fn)
                with open(abspath, 'r') as f_in:
                    # check log content
                    in_lines = set(f_in.read().splitlines())
                    for line in in_lines:
                        nt.assert_true(line in out_lines)
                # also check file name
                nt.assert_true(fn in out_lines)

        # test overwriting a zip
        mt.consolidate_logs(work_dir, output_fn, overwrite=True, remove_original=False,
                            zip_file=True)
        nt.assert_true(os.path.exists(output_gz))

        # test removing input files when a log is made
        for fn in input_files:
            abspath = os.path.join(work_dir, fn)
            nt.assert_true(os.path.exists(abspath))

        mt.consolidate_logs(work_dir, output_fn, overwrite=True, remove_original=True)

        # make sure that original files are now gone
        for fn in input_files:
            abspath = os.path.join(work_dir, fn)
            nt.assert_false(os.path.exists(abspath))

        # clean up after ourselves
        os.remove(output_fn)
        os.remove(output_fn + '.gz')

        return

    def test_consolidate_logs_errors(self):
        # define args
        input_dir = os.path.join(DATA_PATH, 'test_input')
        work_dir = os.path.join(DATA_PATH, 'test_output')
        output_fn = os.path.join(DATA_PATH, 'test_output', 'mf.log')

        # copy input files over to output directory
        input_files = [f for f in os.listdir(input_dir) if f[-4:] == '.log']
        for fn in input_files:
            abspath = os.path.join(input_dir, fn)
            shutil.copy(abspath, work_dir)

        # create single log file from input logs
        if os.path.exists(output_fn):
            os.remove(output_fn)
        mt.consolidate_logs(work_dir, output_fn, remove_original=False, zip_file=False)

        # make sure that we raise an error if we don't pass overwrite=True
        nt.assert_raises(IOError, mt.consolidate_logs, work_dir, output_fn, overwrite=False)

        # test making a zip
        mt.consolidate_logs(work_dir, output_fn, overwrite=True, remove_original=False,
                            zip_file=True)

        # check that file exists
        output_gz = output_fn + '.gz'
        nt.assert_true(os.path.exists(output_gz))

        # make sure we get an error if the file exists
        nt.assert_raises(IOError, mt.consolidate_logs, work_dir, output_fn, overwrite=False,
                         zip_file=True)

        # clean up after ourselves
        for fn in input_files:
            abspath = os.path.join(work_dir, fn)
            os.remove(abspath)
        os.remove(output_gz)

        return
