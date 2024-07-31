from __future__ import annotations
from pathlib import Path
import toml
from ..data import DATA_PATH
import pytest
from hera_opm import mf_tools as mt
import shutil

hera_cal = pytest.importorskip("hera_cal")


def make_lstbin_config_file(
    fl: Path,
    datafiles: dict | list,
    notebook: bool = False,
    options=None,
    lstbin_opts=None,
    file_cfg=None,
    lstavg_opts=None,
    bl_chunk_size: int | None = 5000,
):
    """Make a lstbin config file."""
    options = {
        **{
            "makeflow_type": "lstbin",
            "path_to_do_scripts": "/an/unused/path/for/tests",
            "source_script": "~/.bashrc",
            "conda_env": "hera",
            "base_mem": 10000,
            "base_cpu": 1,
        },
        **(options or {}),
    }

    lstbin_opts = {
        **{
            "parallelize": True,
            "outdir": str(fl.parent),
            "parent_dir": str(fl.parent),
            "bl_chunk_size": bl_chunk_size,
        },
        **(lstbin_opts or {}),
    }

    file_cfg = {
        **{
            "nlsts_per_file": 60,
            "lst_start": 0.0,
            "datafiles": datafiles,
        },
        **(file_cfg or {}),
    }

    if isinstance(datafiles, list):
        file_cfg["datadir"] = str(DATA_PATH)

    lstavg_opts = {
        **{
            "outdir": "../data",
            "fname_format": "{inpaint_mode}/zen.{kind}.{lst:7.5f}.sum.uvh5",
            "overwrite": True,
            "write_med_mad": True,
            "rephase": False,
        },
        **(lstavg_opts or {}),
    }

    if notebook:
        action = "PER_OUTFILE_LSTSTACK_METRICS_NOTEBOOK"
        args = [
            "outdir",
            "lstconf",
            "lstavg_toml_file",
            "output_file_select",
            "kernel",
        ]
    else:
        action = "LSTBIN"
        args = [
            "lstconf",
            "lstavg_toml_file",
            "output_file_select",
        ]

    tomldict = {
        "Options": options,
        "LSTBIN_OPTS": lstbin_opts,
        "FILE_CFG": file_cfg,
        "LSTAVG_OPTS": lstavg_opts,
        "WorkFlow": {"actions": [action]},
        action: {"args": args},
    }

    with open(fl, "w") as fl:
        toml.dump(tomldict, fl)


@pytest.fixture(scope="module")
def lsttoml_direct_datafiles(tmp_path_factory) -> Path:
    """Make a direct lstbin config file."""
    fl = tmp_path_factory.mktemp("data") / "lstbin_direct.toml"
    make_lstbin_config_file(
        fl, datafiles=["zen.2458043.40141.HH.uvh5", "zen.2458043.40887.HH.uvh5"]
    )
    return fl


@pytest.fixture(scope="module")
def lsttoml_direct_datafiles_blchunk_none(tmp_path_factory) -> Path:
    """Make a direct lstbin config file."""
    fl = tmp_path_factory.mktemp("data") / "lstbin_direct.toml"
    make_lstbin_config_file(
        fl,
        datafiles=["zen.2458043.40141.HH.uvh5", "zen.2458043.40887.HH.uvh5"],
        bl_chunk_size=None,
    )
    return fl


@pytest.fixture(scope="module")
def lsttoml_direct_datafiles_glob(tmp_path_factory) -> Path:
    """Make a direct lstbin config file."""
    fl = tmp_path_factory.mktemp("data") / "lstbin_direct.toml"
    make_lstbin_config_file(
        fl,
        datafiles=[
            "zen.2458043.*.HH.uvh5",
            "zen.2458044.*.HH.uvh5",
            "zen.2458045.*.HH.uvh5",
        ],
    )
    return fl


@pytest.fixture(scope="module")
def datafiles_in_nightly_folders(tmp_path_factory) -> Path:

    topdir = tmp_path_factory.mktemp("nightly-data")

    # Also, put our input files into nightly folders
    for night in ["2458043", "2458044", "2458045"]:
        ndir = topdir / night
        ndir.mkdir()

        for fl in Path(DATA_PATH).glob("zen.*.uvh5"):
            if f"{night}." in fl.name:
                shutil.copy(fl, ndir / fl.name)

    return topdir


@pytest.fixture(scope="module")
def lsttoml_notebook_datafiles(
    tmp_path_factory, datafiles_in_nightly_folders: Path
) -> Path:
    """Make a notebook lstbin config file."""
    fl = tmp_path_factory.mktemp("data") / "lstbin_notebook.toml"
    make_lstbin_config_file(
        fl,
        datafiles={
            "datadir": str(datafiles_in_nightly_folders),
            "nights": [fl.name for fl in datafiles_in_nightly_folders.glob("*")],
            "fileglob": "{night}/zen.{night}.*.HH.uvh5",
        },
        notebook=True,
    )
    return fl


@pytest.mark.parametrize(
    "config_file",
    [
        "lsttoml_direct_datafiles",
        "lsttoml_direct_datafiles_blchunk_none",
        "lsttoml_direct_datafiles_glob",
        "lsttoml_notebook_datafiles",
    ],
)
@pytest.mark.parametrize("give_mf_name", [True, False])
def test_build_makeflow_from_config_lstbin_options(
    config_file,
    tmp_path_factory,
    request,
    give_mf_name,
):
    """Test building a makeflow from a lstbin config file.

    In particular, this function calls the build_makeflow_from_config directly,
    which dispatches to the build_lstbin_makeflow_from_config function.
    """
    config_file = request.getfixturevalue(config_file)

    # test lstbin version with options
    obsids = None
    work_dir = tmp_path_factory.mktemp("test_output")
    outfile = work_dir / config_file.name.replace(".toml", ".mf")

    mt.build_makeflow_from_config(
        obsids,
        config_file,
        mf_name=outfile.name if give_mf_name else None,
        work_dir=work_dir,
        outdir=work_dir,  # pass directly so that we can check the output
    )

    # make sure the output files we expected appeared
    assert outfile.exists()
