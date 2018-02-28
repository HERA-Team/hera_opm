# Task Scripts

**Task scripts** are the fundamental units of the analysis pipeline. They
represent individual steps taken, and should be atomic. There is negligible
overhead associated with adding steps, and tracking where exactly somthing goes
wrong is easier for smaller tasks sizes. It also allows for easier checkpointing
in the event that something crashes or exits early. At the same time, task
scripts can call several commands or programs, with no restriction on their
size. Just try to find the right balance bewteen ease of segmenting out tasks,
and pain of having to restart a given task.

Task scripts are assumed to be bash scripts. These in turn can call python
scripts (such as analysis routines or uploading files to the librarian), or
perform housekeeping (such as removing files once uploaded to the librarian, and
no longer needed locally) using shell builtins. Note that these bash scripts
typically run in new environments, and any commonly-used custom functions must
be loaded as part of the script. Anaconda environments must also be loaded,
though the `hera_opm` package provides support for this, and so writing this into
the task scripts is not necessary.

## Naming Convention

There is a strict naming convention for task scripts. Suppose that a step in the
analysis pipeline is called "FOO". The associated task script *must* be called
`do_FOO.sh`. Further, it is assumed that all of the task scripts will reside in
the same directory (though it need not be the same directory as the files to be
analyzed). Note that as part of the execution of the pipeline, `makeflow` will
check for the existence of the task scripts, and halt with an error if it is not
found.

## Output

Task scripts usually, though not always, produce some type of output
file. However, it is not strictly a requirement. Also note that any output files
produced by the analysis pipeline will persist, unless explicitly deleted as
part of the pipeline. Also, stdout and stderr for a given step will be saved to
a single file, and utilities exist for combining these into a single log once
processing has been completed.


## Polarization

A significant design requirement for the `hera_opm` module is to provide support
for the fact that not all 4 polarizations of the raw data are contained in a
single file. `hera_opm` is polarization-aware, in the sense that the user can
pass in a list of polarizations to apply the analysis steps to. However, the
user is still responsible for writing the task scripts in a way that handles the
polarization.

As an example, the script below is the `do_ANT_METRICS.sh` task script used in
the H1C RTP system:

```bash
#! /bin/bash
set -e

# import common functions
src_dir="$(dirname "$0")"
source ${src_dir}/_common.sh

# run script from hera_qm
fn=$(basename $1 uv)

# define polarizations
pol1="xx"
pol2="yy"
pol3="xy"
pol4="yx"

# we only want to run this script for the "xx" thread
if is_same_pol $fn $pol1; then
    # make comma-separated list of polarizations
    pols=$(join_by , $pol1 $pol2 $pol3 $pol4)

    # make new filenames for polarizations
    fn1=$(replace_pol $fn $pol1)
    fn2=$(replace_pol $fn $pol2)
    fn3=$(replace_pol $fn $pol3)
    fn4=$(replace_pol $fn $pol4)

    echo ant_metrics_run.py -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.json --vis_format=miriad ${fn1}HH.uv ${fn2}HH.uv ${fn3}HH.uv ${fn4}HH.uv
    ant_metrics_run.py -p $pols --crossCut=5 --deadCut=5 --extension=.ant_metrics.json --vis_format=miriad ${fn1}HH.uv ${fn2}HH.uv ${fn3}HH.uv ${fn4}HH.uv
fi
```

The `is_same_pol` function is defined in `_common.sh`, and checks to see if the
string `$pol1` is in `$fn`. In this case, we are checking to see if `xx` is in
the filename. If it is, then the body of the `if` clause is executed. Otherwise,
no action is taken. Accordingly, the `ant_metrics_run.py` script is *only*
called by a single polarization, though it requires all 4 polarizations as
input. The `_common.sh` file is
[here](https://github.com/HERA-Team/RTP/blob/master/scripts/hera/_common.sh),
and is helpful for building task scripts which can handle polarization.
