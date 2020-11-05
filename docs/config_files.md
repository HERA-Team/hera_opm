# Config Files

**Config files** are the means by which a pipeline is defined. Their primary
purpose is to enumerate all of the steps in a pipeline, and to list requirements
for individual steps. They also define general options that are assumed for all
stages in the pipeline.

# Format

Config files are written in [TOML](https://en.wikipedia.org/wiki/TOML),
reminiscent of UNIX configuration files. This results in files where are easily
human-readable, as well as machine-parsable. Below we enumerate the most salient
parts of the file.

## Options

The `Options` section specifies general settings that apply to the entire
workflow. We list several below, but the list is by no means exhaustive.

### path_to_do_scripts

This lists the absolute path to the task scripts (also called "do_scripts" due
to their naming convention).

### conda_env

The name of a conda environment that should be activated before running each
analysis step.

### base_mem

The default memory requirement for each step in the workflow, in MB. Individual
steps can request a different amount of memory (e.g., if one step requires
significantly more memory than the other ones).

### base_cpu

The default number of CPUs for each processing stage. Unless you have explicitly
made your task parallel (using OpenMP, MPI, or other parallelization framework),
this should be 1.


## WorkFlow

This section defines the steps present in the pipeline.

### actions

The pipeline steps, separated by commas (and optionally spaces). This defines
steps of analysis steps, which will be performed exactly in order. This section
can span multiple lines, but cannot be separated by blank lines.

## Action Steps

Each task named in the `WorkFlow::actions` section must have its own
corresponding entry. The only required entry is `args`, which specifies the
arguments to pass to the corresponding task script. For the purpose of building
the task names, there is a "replacement mini-language" based on the input names
of the files.

### args

The arguments that should be passed in to the corresponding task script. See the
Replacement section below for further explanation.

### prereqs

Pre-requisite steps where a previous step in
the workflow must complete for a given file and all of its time neighbors. The
chunking keywords listed below are used to determine which files are primary
obsids for a given file, and hence which steps must be completed before
launching a particular task script.

### Time Chunking

When running a workflow, it is sometimes desirable to operate on several files
contiguous in time as a single chunk. There are several options that control how
a full list of files is partitioned into a series of time-contiguous chunks that
are all operated on together as a single job in the workflow, referred to as a
"time chunk". When evaluating the workflow to determine which obsids to operate
on, the code defines a notion of "primary obsids". For each primary obsid, a
task script is run. Each obsid could be a primary obsid.  However, it is also
possible to partition the list such that, e.g., every tenth file is a primary
obsid, and the others do not have corresponding task scripts generated for
them. The specific keywords that may be specified are:

* `chunk_size`: the total size of a given time chunk, in terms of the number of
  files. In addition to an integer, can also be the string `"all"` to indicate
  the chunk includes all time values.
* `time_centered`: whether to treat a chunk of files such that the primary obsid
  is in the center the chunk (True), or the start of the chunk. If
  `time_centered` is `True` and `chunk_size` is even, an extra entry is included
  on the left to make the chunk symmetric about the chunk center. Default is
  `True`.
* `stride_length`: the number of obsids to stride by when generating the list of
  primary obsids. For example, if `stride_length = 10`, `chunk_size=10`, and
  `time_centered` is `False`, the list will be partitioned into chunks 10 files
  long with no overlap. Default is 1 (i.e., every obsid will be treated as a
  primary obsid with the exception of those files within `chunk_size` of
  the edge).
* `collect_stragglers`: determine how to handle lists that are not evenly
  divided by `stride_length`. If True, any files that would not evenly be added
  to a full group are instead added to the second-to-last group to make an
  "extra large" group, ensuring that all files are accounted for when
  processing. If False, these obsids will not be included in the list. Default
  is False.
* `prereq_chunk_size`: this option is specified if the user wants to wait for
  specific entries in the previous step to finish before starting the current
  one, without necessarily using them. Usually this will not be set, or it will
  be `"all"` to indicate all entries for the previous step must be completed
  before proceeding.


### mem

The required memory for each task, in MB. This is for scheduling purposes to
avoid oversaturating computational resources available. However, on local
compute environments, there is no hard limit imposed (that is, if your task
requires more memory than the amount specified, it is not killed). That said, it
is better to overestimate the memory required, to avoid instances of tasks
having insufficient memory, and terminating early.

### ncpu

The number of CPU cores that should be reserved for a given task. Unless you
have explicitly made your task parallel (using OpenMP, MPI, or other
parallelization framework), this should always be 1.


### Replacement

One of the entries replaced in the `args` section is `{basename}` (that exact
string, including the curly braces), which is the root name of the file. For
instance, if the obsid specified when constructing the makeflow file is
`zen.2458000.12345.xx.uv`, then this name will be replaced anytime `{basename}`
is encountered in the `args`. If chunking multiple files using n_time_neighbors,
this argument should instead be replaced with '{obsid_list}', and should be
placed as the last argument in the list.

In addition to the `{basename}` substitution, entries from other parts of the
config file can be substituted. The syntax for this is to use:
```
${Heading:option}
```

For instance, suppose that we want to specify our own list of excluded antennas,
and pass it as an argument to several of our task scripts. Suppose we define:

```
[Options]
ex_ants = /path/to/exants/file.txt
```

Then in the corresponding `args` list for our desired task (say for `FIRSTCAL`),
we can write:

```
[FIRSTCAL]
prereqs = ANT_METRICS
args = {basename}, ${Options:ex_ants}
```

This will be equivalent to calling:
```bash
$ do_FIRSTCAL.sh zen.2458000.12345.xx.HH.uv /path/to/exants/file.txt
```
