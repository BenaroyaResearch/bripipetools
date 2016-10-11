**Note:** during early development (until package is a bit more stable), intermediate patches and bug fixes will only be listed separately in the changelog up to the point of a new major and minor versions &mdash; at that point, they will be lumped together under the major/minor release description

**[v0.3.1](https://github.com/jaeddy/bripipetools/tree/e7aa92d49dae8fa34a463aba68de4ff9610d2af7) - 2016-10-11**

+ New `postprocess` submodule to compile and merge all "stitched" files for different summary output types (e.g., metrics, QC, validations).
+ Modified data import/retrieval functionality with GenLIMS to ensure that timestamp fields (`dateCreated`, `lastUpdated`) are present and correctly set for all objects.

-----

**[v0.3.0](https://github.com/jaeddy/bripipetools/tree/6fffe25dabe85864f50ddd2d09fa66eb185350e0) - 2016-10-07**

+ Documentation! Initial bolus of (fairly skeletal) docs with Sphinx and ReadTheDocs.
+ New `cleanup` postprocessing submodule for organizing/renaming pipeline output files with deprecated structure (only works for FastQC outputs for now).
+ Major overhaul and expanion of test data, updated tests to reflect new data organization/structure.
+ New `io` module to parse and stitch outputs from FastQC.
+ Updated db operations in `genlims` module to reduce code re-use, improve logic.
+ Cleaned up, parametrized, and extended tests for all modules, especially those related to db tasks.
+ Fixed a bug in `dbify` module that skipped QC (i.e., sex check) when importing data from a processing batch.

-----

**[v0.2.0](https://github.com/jaeddy/bripipetools/tree/0d595fc1deed7a1d7ee81d0520097616bd3cbd50) - 2016-09-23**

+ New `validation` module with count-based sex check feature.
+ Inclusion of validation values/information in addition to other outputs for processed library objects.

-----

**[v0.1.0](https://github.com/jaeddy/bripipetools/tree/0d767a60c60a803df934675dfb7d4f36ee5802d7) - 2016-09-22**

+ First unofficial release of **`bripipetools`** package (with setup config and TravisCI implemented). Basic module structure & tests in place, with command-line entrypoints for postprocessing and db import. Still under heavy development.
