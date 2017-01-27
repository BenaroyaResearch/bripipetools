.. _start-page:

***************
Getting started
***************

.. _start-using:

Using bripipetools
==================

Currently, there are three primary functions served by package modules:

- Generation of workflow instructions and submission of data processing batches
- Collection and organization of output data from bioinformatics processing workflows
- Annotation and import of pipeline input & output data into the Genomics Core Mongo database — i.e., **GenLIMS**

These features are continuing to expand and evolve over time.

Workflow batch submission
-------------------------

Batch submission to Globus Galaxy for bioinformatics data processing is currently managed through ``bripipetools submit`` command, which uses the ``submission`` package.

Post-processing
---------------

The entrypoint for tasks related to organizing processing output files (e.g., file stitching, cleanup, etc.) is the ``bripipetools postprocess`` command, which uses the ``postprocess`` package.

Data management
---------------

Annotation of sequencing and processing data — as well as corresponding retrieval and import of data from/to the GenLIMS database — is performed through the ``bripipetools dbify`` command, which uses the ``dbify`` package.

-----


.. _start-install:

Installing bripipetools
=======================

::

    git clone https://github.com/BenaroyaResearch/bripipetools
    conda env create -n bripipetools environment.yml


For development::

    pip install -e .
    py.test
    bripipetools

For production (not currently tested)::

    pip install .
    python setup.py test

