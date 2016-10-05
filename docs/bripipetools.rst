bripipetools
============

**bripipetools** (i.e., BRI Pipeline Tools) is a collection of modules for managing the operation of processing workflows --- as well as the input and output data for these workflows --- within the Genomics and Bioinformatics Cores at the Benaroya Research Institute.

.. note:: Scope & environment

    These tools are designed with **very** strong assumptions about data structure and formats, as well as available resources (e.g., file system, database). While bits and pieces of the code may be useful in other contexts, as a general rule, if you try to install/use this package somewhere other than one of a handful of properly configured BRI servers, *you're going to have a bad time*.

Using bripipetools
------------------

Currently, there are three primary functions served by package modules:

- Generation of workflow instructions and submission of data processing batches
- Collection and organization of output data from bioinformatics processing workflows
- Annotation and import of pipeline input & output data into the Genomics Core Mongo database --- i.e., **GenLIMS**

These features are continuing to expand and evolve over time.
