"""Tests for mf_tools.py"""
import nose.tools as nt
import os
import shutil
import gzip
import glob
from hera_opm.data import DATA_PATH
import hera_opm.mf_tools as mt
import ConfigParser as configparser
from configparser import ConfigParser, ExtendedInterpolation


class TestMethods(object):
    def setUp(self):
        self.config_file = os.path.join(DATA_PATH, 'sample_config', 'nrao_rtp.cfg')
        self.config_file_time_neighbors = os.path.join(DATA_PATH, 'sample_config', 'nrao_rtp_time_neighbors.cfg')
        self.config_file_options = os.path.join(DATA_PATH, 'sample_config', 'nrao_rtp_options.cfg')
        self.config_file_lstbin = os.path.join(DATA_PATH, 'sample_config', 'lstbin.cfg')
        self.config_file_lstbin_options = os.path.join(DATA_PATH, 'sample_config', 'lstbin_options.cfg')
        self.bad_config_file = os.path.join(DATA_PATH, 'sample_config', 'bad_example.cfg')
        self.obsids_pol = ['zen.2457698.40355.xx.HH.uvcA', 'zen.2457698.40355.xy.HH.uvcA',
                           'zen.2457698.40355.yx.HH.uvcA', 'zen.2457698.40355.yy.HH.uvcA']
        self.obsids_nopol = ['zen.2457698.40355.HH.uvcA']
        self.obsids_lstbin = [sorted(glob.glob(DATA_PATH + '/zen.245804{}.*.xx.HH.uvXRAA'.format(i))) for i in [3,4,5]]
        self.pols = ['xx', 'xy', 'yx', 'yy']
        self.obsids_time = ['zen.2457698.30355.xx.HH.uvcA', 'zen.2457698.40355.xx.HH.uvcA',
                            'zen.2457698.50355.xx.HH.uvcA']
        return

    def test_get_jd(self):
        # send in a sample file name
        filename = "zen.2458000.12345.xx.HH.uv"
        jd = mt.get_jd(filename)
        nt.assert_true(jd, "2458000")
        return

    def test_get_config_entry(self):
        # retreive config
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(self.config_file)

        # retrieve specific entry
        header = 'OMNICAL'
        item = 'prereqs'
        nt.assert_equal("FIRSTCAL_METRICS", mt.get_config_entry(config, header, item))

        # get nonexistent, but not required, entry
        header = 'OMNICAL'
        item = 'blah'
        nt.assert_equal(None, mt.get_config_entry(config, header, item, required=False))

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

    def test_make_time_neighbor_outfile_name(self):
        # define args
        obsid = self.obsids_time[1]
        action = 'OMNICAL'
        pol = self.pols[3]
        outfiles = ['zen.2457698.30355.xx.HH.uvcA.OMNICAL.yy.out',
                    'zen.2457698.40355.xx.HH.uvcA.OMNICAL.yy.out',
                    'zen.2457698.50355.xx.HH.uvcA.OMNICAL.yy.out']
        nt.assert_equal(set(outfiles), set(mt.make_time_neighbor_outfile_name(obsid, action, self.obsids_time, pol)))

        # test asking for "all" neighbors
        nt.assert_equal(set(outfiles), set(mt.make_time_neighbor_outfile_name(obsid, action, self.obsids_time, pol,
                                                                              n_neighbors='all')))

        # test edge cases
        obsid = self.obsids_time[0]
        nt.assert_equal(set(outfiles[:2]), set(mt.make_time_neighbor_outfile_name(obsid, action, self.obsids_time, pol)))
        obsid = self.obsids_time[2]
        nt.assert_equal(set(outfiles[1:]), set(mt.make_time_neighbor_outfile_name(obsid, action, self.obsids_time, pol)))

        # run for no polarizations
        obsid = self.obsids_time[1]
        outfiles = set(['zen.2457698.30355.xx.HH.uvcA.OMNICAL.out',
                        'zen.2457698.40355.xx.HH.uvcA.OMNICAL.out',
                        'zen.2457698.50355.xx.HH.uvcA.OMNICAL.out'])
        nt.assert_equal(outfiles, set(mt.make_time_neighbor_outfile_name(obsid, action, self.obsids_time)))
        return

    def test_make_time_neighbor_outfile_name_errors(self):
        # test not having the obsid in the supplied list
        obsid = 'zen.1234567.12345.xx.HH.uvcA'
        action = 'OMNICAL'
        nt.assert_raises(ValueError, mt.make_time_neighbor_outfile_name, obsid, action, self.obsids_time)

        # test passing in nonsense for all_neighbors
        nt.assert_raises(ValueError, mt.make_time_neighbor_outfile_name, self.obsids_time[0], action,
                         self.obsids_time, pol='xx', n_neighbors='blah')

        # test passing in a negative number of neighbors
        nt.assert_raises(ValueError, mt.make_time_neighbor_outfile_name, self.obsids_time[0], action,
                         self.obsids_time, pol='xx', n_neighbors='-1')

        return

    def test_prep_args(self):
        # define args
        obsid = self.obsids_pol[0]
        args = '{basename}'
        pol = self.pols[3]
        output = 'zen.2457698.40355.yy.HH.uvcA'
        nt.assert_equal(output, mt.prep_args(args, obsid, pol))

        # test requesting polarization, but none found in file
        obsid = 'zen.2457698.40355.uv'
        nt.assert_equal(obsid, mt.prep_args(args, obsid, pol))

        # test not requesting polarization
        obsid = self.obsids_pol[0]
        output = 'zen.2457698.40355.xx.HH.uvcA'
        nt.assert_equal(output, mt.prep_args(args, obsid))

        # test having time-adjacent keywords
        obsid = self.obsids_time[1]
        obsids = self.obsids_time
        args = '{basename} {prev_basename} {next_basename}'
        output = 'zen.2457698.40355.xx.HH.uvcA zen.2457698.30355.xx.HH.uvcA zen.2457698.50355.xx.HH.uvcA'
        nt.assert_equal(output, mt.prep_args(args, obsid, obsids=obsids))

        # test edge cases
        obsid = self.obsids_time[0]
        output = 'zen.2457698.30355.xx.HH.uvcA None zen.2457698.40355.xx.HH.uvcA'
        nt.assert_equal(output, mt.prep_args(args, obsid, obsids=obsids))

        obsid = self.obsids_time[2]
        output = 'zen.2457698.50355.xx.HH.uvcA zen.2457698.40355.xx.HH.uvcA None'
        nt.assert_equal(output, mt.prep_args(args, obsid, obsids=obsids))

        return

    def test_prep_args_errors(self):
        # define args
        obsid = self.obsids_time[0]
        obsids = self.obsids_pol
        args = '{basename} {prev_basename}'
        nt.assert_raises(ValueError, mt.prep_args, args, obsid)
        nt.assert_raises(ValueError, mt.prep_args, args, obsid, obsids=obsids)

        args = '{basename} {next_basename}'
        nt.assert_raises(ValueError, mt.prep_args, args, obsid)
        nt.assert_raises(ValueError, mt.prep_args, args, obsid, obsids=obsids)

        return

    def test_build_analysis_makeflow_from_config(self):
        # define args
        obsids = self.obsids_pol[:1]
        config_file = self.config_file
        work_dir = os.path.join(DATA_PATH, 'test_output')

        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

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
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        # also test providing the name of the output file
        mf_output = "output.mf"
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_analysis_makeflow_from_config(obsids, config_file, mf_name=outfile, work_dir=work_dir)

        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        return

    def test_build_analysis_makeflow_from_config_time_neighbors(self):
        # define args
        obsids = self.obsids_time
        config_file = self.config_file_time_neighbors
        work_dir = os.path.join(DATA_PATH, 'test_output')

        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

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
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        return

    def test_build_analysis_makeflow_from_config_errors(self):
        # define args
        obsids = self.obsids_pol[:2]
        config_file = self.config_file
        work_dir = os.path.join(DATA_PATH, 'test_output')

        # raise an error for passing in obsids with different polarizations
        nt.assert_raises(AssertionError, mt.build_analysis_makeflow_from_config, obsids,
                         config_file, work_dir=work_dir)

        # raise an error for passing in an obsid with no polarization string
        obsids = ['zen.2458000.12345.uv']
        nt.assert_raises(AssertionError, mt.build_analysis_makeflow_from_config, obsids,
                         config_file, work_dir=work_dir)

        return

    def test_build_analysis_makeflow_from_config_options(self):
        # define args
        obsids = self.obsids_pol[:1]
        config_file = self.config_file_options
        work_dir = os.path.join(DATA_PATH, 'test_output')

        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_analysis_makeflow_from_config(obsids, config_file, work_dir=work_dir)

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
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        # also test providing the name of the output file
        mf_output = "output.mf"
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_analysis_makeflow_from_config(obsids, config_file, mf_name=outfile, work_dir=work_dir)

        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        return

    def test_build_lstbin_makeflow_from_config(self):
        # define load in config
        config_file = self.config_file_lstbin
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(config_file)

        # overwrite parent dir
        config["LSTBIN_OPTS"]["parent_dir"] = DATA_PATH

        # setup vars
        work_dir = os.path.join(DATA_PATH, 'test_output')
        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_lstbin_makeflow_from_config(config, mf_name='lstbin.mf', work_dir=work_dir)

        # make sure the output files we expected appeared
        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        # also test providing the name of the output file
        mf_output = "output.mf"
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_lstbin_makeflow_from_config(config, mf_name=outfile, work_dir=work_dir)

        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        return

    def test_build_lstbin_makeflow_from_config_options(self):
        # define args
        obsids = self.obsids_lstbin
        config_file = self.config_file_lstbin_options
        work_dir = os.path.join(DATA_PATH, 'test_output')

        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_lstbin_makeflow_from_config(obsids, config_file, work_dir=work_dir)

        # make sure the output files we expected appeared
        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        # also test providing the name of the output file
        mf_output = "output.mf"
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_lstbin_makeflow_from_config(obsids, config_file, mf_name=outfile, work_dir=work_dir)

        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        return

    def test_build_makeflow_from_config(self):
        # define args
        obsids = self.obsids_pol[:1]
        config_file = self.config_file
        work_dir = os.path.join(DATA_PATH, 'test_output')

        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_makeflow_from_config(obsids, config_file, work_dir=work_dir)

        # make sure the output files we expected appeared
        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        # also test lstbin version
        obsids = self.obsids_lstbin
        config_file = self.config_file_lstbin
        mf_output = os.path.splitext(os.path.basename(config_file))[0] + '.mf'
        outfile = os.path.join(work_dir, mf_output)
        if os.path.exists(outfile):
            os.remove(outfile)
        mt.build_makeflow_from_config(obsids, config_file, work_dir=work_dir)

        # make sure the output files we expected appeared
        nt.assert_true(os.path.exists(outfile))

        # clean up after ourselves
        os.remove(outfile)
        mt.clean_wrapper_scripts(work_dir)

        # ensure we raise an error when no makeflow_type is specified
        config_file = self.bad_config_file
        nt.assert_raises(ValueError, mt.build_makeflow_from_config, obsids, config_file, work_dir=work_dir)

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
