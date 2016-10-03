**Note:** during early development (until package is a bit more stable), intermediate patches and bug fixes will only be listed separately in the changelog up to the point of a new major and minor versions &mdash; at that point, they will be lumped together under the major/minor release description

**[v0.2.3](https://github.com/jaeddy/bripipetools/tree/bf49b25370ecf41543b7e2f4ee563e5f6ce22e89) - 2016-10-03**

+ Major overhaul and expanion of test data, updated tests to reflect new data organization/structure
+ New `io` module to parse and stitch outputs from FastQC

**[v0.2.2](https://github.com/jaeddy/bripipetools/tree/4db1881f056e328a5e8397e4a99a09609850f006) - 2016-09-28**

+ Updated db operations in `genlims` module to reduce code re-use, improve logic
+ Cleaned up, parametrized, and extended tests for all modules, especially those related to db tasks

**[v0.2.1](https://github.com/jaeddy/bripipetools/tree/9382caab9d0a08ffbce237283848875eb3b34447) - 2016-09-23**

+ Fixed a bug in `dbify` module that skipped QC (i.e., sex check) when importing data from a processing batch.

**[v0.2.0](https://github.com/jaeddy/bripipetools/tree/0d595fc1deed7a1d7ee81d0520097616bd3cbd50) - 2016-09-23**

+ New `validation` module with count-based sex check feature.
+ Inclusion of validation values/information in addition to other outputs for processed library objects.

-----

**[v0.1.0](https://github.com/jaeddy/bripipetools/tree/0d767a60c60a803df934675dfb7d4f36ee5802d7) - 2016-09-22**

+ First unofficial release of **`bripipetools`** package (with setup config and TravisCI implemented). Basic module structure & tests in place, with command-line entrypoints for postprocessing and db import. Still under heavy development.
