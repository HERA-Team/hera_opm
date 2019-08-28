"""Script for installing hera_opm."""
import json
import os
import sys
from glob import glob

from setuptools import setup

sys.path.append("hera_opm")
import version  # noqa

data = [
    version.git_origin,
    version.git_hash,
    version.git_description,
    version.git_branch,
]
with open(os.path.join("hera_opm", "GIT_INFO"), "w") as outfile:
    json.dump(data, outfile)


def package_files(package_dir, subdirectory):
    """Walk the input package_dir/subdirectory to generate a package_data list.

    Parameters
    ----------
    package_dir : str
        Path to the package directory.
    subdirectory : str
        The subdirectory to investigate.

    Returns
    -------
    paths : list of str
        A list containing all of the relevant package_data.
    
    """
    paths = []
    directory = os.path.join(package_dir, subdirectory)
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            path = path.replace(package_dir + "/", "")
            paths.append(os.path.join(path, filename))
    return paths


data_files = package_files("hera_opm", "data")

setup_args = {
    "name": "hera_opm",
    "author": "HERA Team",
    "url": "https://github.com/HERA-Team/hera_opm",
    "license": "BSD",
    "description": "offline-processing and pipeline managment for HERA data analysis",
    "package_dir": {"hera_opm": "hera_opm"},
    "packages": ["hera_opm"],
    "include_package_data": True,
    "scripts": glob("scripts/*.py") + glob("scripts/*.sh"),
    "version": version.version,
    "package_data": {"hera_opm": data_files},
    "install_requires": ["toml>=0.9.4", "six"],
    "zip_safe": False,
    "setup_requires": ["pytest-runner", "toml>=0.9.4", "six"],
    "tests_require": ["pytest", "toml>=0.9.4", "six"],
}

if __name__ == "__main__":
    setup(**setup_args)
