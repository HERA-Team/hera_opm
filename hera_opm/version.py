# -*- coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD license
"""Module for generating version info."""

import json
import os
import subprocess


def construct_version_info():
    """Make version info using git.

    Parameters
    ----------
    None

    Returns
    -------
    version_info : dict
        Dictionary containing version information as key-value pairs.

    """
    hera_opm_dir = os.path.dirname(os.path.realpath(__file__))

    def get_git_output(args, capture_stderr=False):
        """Get output from Git.

        This function ensures that it is of the ``str`` type, not bytes.

        Parameters
        ----------
        args : list of str
            A list of arguments to be passed to `git`.
        capture_stderr : bool
            Whether to capture standard error as part of the call to git.

        Returns
        -------
        data : str
            The output of the git command as `str` type.

        """
        argv = ["git", "-C", hera_opm_dir] + args

        if capture_stderr:
            data = subprocess.check_output(argv, stderr=subprocess.STDOUT)
        else:
            data = subprocess.check_output(argv)

        data = data.strip()

        return data.decode("utf-8")

    def unicode_to_str(u):
        return u  # pragma: no cover

    version_file = os.path.join(hera_opm_dir, "VERSION")
    version = open(version_file).read().strip()

    try:
        git_origin = get_git_output(
            ["config", "--get", "remote.origin.url"], capture_stderr=True
        )
        git_hash = get_git_output(["rev-parse", "HEAD"], capture_stderr=True)
        git_description = get_git_output(["describe", "--dirty", "--tag", "--always"])
        git_branch = get_git_output(
            ["rev-parse", "--abbrev-ref", "HEAD"], capture_stderr=True
        )
    except subprocess.CalledProcessError:  # pragma: no cover
        try:
            # Check if a GIT_INFO file was created when installing package
            git_file = os.path.join(hera_opm_dir, "GIT_INFO")
            with open(git_file) as data_file:
                data = [unicode_to_str(x) for x in json.loads(data_file.read().strip())]
                git_origin = data[0]
                git_hash = data[1]
                git_description = data[2]
                git_branch = data[3]
        except (IOError, OSError):
            git_origin = ""
            git_hash = ""
            git_description = ""
            git_branch = ""

    version_info = {
        "version": version,
        "git_origin": git_origin,
        "git_hash": git_hash,
        "git_description": git_description,
        "git_branch": git_branch,
    }
    return version_info


version_info = construct_version_info()
version = version_info["version"]
git_origin = version_info["git_origin"]
git_hash = version_info["git_hash"]
git_description = version_info["git_description"]
git_branch = version_info["git_branch"]

# String to add to history of any files written with this version of hera_opm
hera_opm_version_str = "hera_opm version: " + version + "."
if git_hash != "":
    hera_opm_version_str += (
        "  Git origin: "
        + git_origin
        + ".  Git hash: "
        + git_hash
        + ".  Git branch: "
        + git_branch
        + ".  Git description: "
        + git_description
        + "."
    )


def main():  # pragma: no cover
    """Print version information then exit.

    Parameters
    ----------
    None

    Returns
    -------
    None

    """
    print("Version = {0}".format(version))
    print("git origin = {0}".format(git_origin))
    print("git branch = {0}".format(git_branch))
    print("git description = {0}".format(git_description))


if __name__ == "__main__":
    main()  # pragma: no cover
