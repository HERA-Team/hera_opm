# -*- coding: utf-8 -*-
# Copyright (c) 2018 The HERA Collaboration
# Licensed under the 2-clause BSD License
"""Package for generating makeflow scripts from a workflow."""

from . import utils
from . import mf_tools

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    from ._version import version as __version__
except ModuleNotFoundError:  # pragma: no cover
    try:
        __version__ = version("hera_opm")
    except PackageNotFoundError:
        # package is not installed
        __version__ = "unknown"

del version
del PackageNotFoundError

__all__ = ["utils", "mf_tools", "version"]
