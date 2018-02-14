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

### pols

This lists the polarizations to be used, as a comma-separated list.

### path_to_do_scripts

This lists the absolute path to the task scripts (also called "do_scripts" due
to their naming convention).

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

Pre-requisite steps that must be completed (for all polarizations) before a task
is executed. Due to the sequential nature of the pipeline, this option is not
necessary for instances where there is only a single polarization to be
analyzed. However, for instances where multiple polarizations are present, these
actions act as a "barrier" to further progress. For instance, before the `yy`
polarization can run the `firstcal` step, it requires information about excluded
antennas, determined by the `ant_metrics` analysis. This analysis is only
performed for the `xx` task thread (though it requires all 4
polarizations). Therefore, the `yy` pipeline thread may arrive at the `firstcal`
step before the associated `ant_metrics` thread has finished running. By adding
`ANT_METRICS` to the `FIRSTCAL::prereqs` section, we ensure that the
`ANT_METRICS` step has completed for *all* polarization threads before
attempting to execute *any* `FIRSTCAL` steps. This ensures that all
prerequisites have been met in terms of expected output files being produced.

### mem

The required memory for each task. This is for scheduling purposes to avoid
oversaturating computational resources available. However, on local compute
environments, there is no hard limit imposed (that is, if your task requires
more memory than the amount specified, it is not killed). That said, it is
better to overestimate the memory required, to avoid instances of tasks having
insufficient memory, and terminating early. **NOTE**: This feature is not
currently implemented.

### cpu

The number of CPU cores that should be reserved for a given task. Unless you
have explicitly made your task parallel (using OpenMP, MPI, or other
parallelization framework), this should always be 1. **NOTE**: This feature is
not currently implemented.


### Replacement

One of the entries replaced in the `args` section is `{basename}` (that exact
string, including the curly braces), which is the root name of the file. For
instance, if the obsid specified when constructing the makeflow file is
`zen.2458000.12345.xx.uv`, then this name will be replaced anytime `{basename}`
is encountered in the `args`. 

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

