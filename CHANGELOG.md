# Changelog
All notable changes to this project will be documented in this file. Note that
changes below pertain primarily to the core python module, as opposed to the
analysis/lstbin pipelines and workflows.


## Unreleased


## [1.0.0] - 2019-11-21

### Added
- HTCondor added as a batch system.
- Script for launching an RTP daily workflow added.
- Slurm added as a batch system.
- `setup` and `teardown` step features added.
- Script for automatically launching workflows for a series of JDs added.
- Support for python 3 added.
- Add option to specifying a job timeout.
- Support for LST-binning pipeline added.

### Changed
- Drop support for python2.
- `black` formatting applied to repo.
- Change how errors logs for jobs are handled.

### Fixed
- Fix support for handling of PBS options.

### Changed
- Codebase supports python3 only.


## [0.1.1] - 2018-02-28

### Added
- Continuous integration support using TravisCI added.

### Fixed
- A bug in output script naming was fixed.

## [0.1] - 2018-02-27

### Added
- Initial versioned release. Earlier changes available in git history.
