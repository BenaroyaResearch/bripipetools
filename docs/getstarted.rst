.. _start-page:

***************
Getting started
***************

.. _start-install:

Installing bripipetools
=======================

To install bripipetools, you'll first need to install a copy of Anaconda by following the instructions at `<https://docs.conda.io/projects/conda/en/latest/user-guide/install/>`_. Once you have Anaconda installed, you can execute the following commands::

    git clone https://github.com/BenaroyaResearch/bripipetools
    conda env create -n bripipetools environment.yml
    conda activate bripipetools


After the Anaconda environment has been set up with the required packages and activated, you can install ``bripipetools``. There are two ways of installing; currently it is recommended that you use the first method, designed to install while the package is undergoing active development::

    pip install -e .
    py.test

There is also an installation method designed for production::

    pip install .
    python setup.py test
    
Following successful installation, you should be able to run the command ``bripipetools`` to see usage information.

-----

.. _start-using:

Using bripipetools
==================

Currently, there are three primary functions served by package modules:

- Generation of workflow instructions and submission of data processing batches
- Collection and organization of output data from bioinformatics processing workflows
- Annotation and import of pipeline input & output data into Mongo databases — i.e., the **Research Database**

These features are continuing to expand and evolve over time.

Workflow batch submission
-------------------------

Batch submission to Globus Galaxy for bioinformatics data processing is currently managed through ``bripipetools submit`` command, which uses the ``submission`` package.

Workflow batch data summarization
---------------------------------

Following a successful submission and completion of a Globus Galaxy batch of jobs, the data can be summarized and inserted into the Research Database using the ``bripipetools wrapup`` command, which uses the packages described below.

Quality control
---------------

Quality control functions (for example, sexchecking) are accessed using the ``bripipetools qc``, which accepts a path to a workflowbatch file and performs the appropriate analyses for the data listed in the batch file.

Post-processing
---------------

The entrypoint for tasks related to organizing processing output files (e.g., file stitching, cleanup, etc.) is the ``bripipetools postprocess`` command, which uses the ``postprocess`` package.

Data management
---------------

Annotation of sequencing and processing data — as well as corresponding retrieval and import of data from/to the Research Database — is performed through the ``bripipetools dbify`` command, which uses the ``dbify`` package.




