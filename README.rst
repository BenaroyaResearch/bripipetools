
.. image:: https://img.shields.io/travis/BenaroyaResearch/bripipetools.svg
        :target: https://travis-ci.org/BenaroyaResearch/bripipetools

.. image:: https://img.shields.io/coveralls/BenaroyaResearch/bripipetools.svg
        :target: https://coveralls.io/github/BenaroyaResearch/bripipetools

.. image:: https://readthedocs.org/projects/bripipelinetools/badge/?version=latest
        :target: http://bripipelinetools.readthedocs.io/en/latest/?badge=latest


bripipetools
============

**bripipetools** (i.e., BRI Pipeline Tools) is a collection of packages for managing the operation of processing workflows — as well as the input and output data for these workflows — within the Genomics and Bioinformatics Cores at the Benaroya Research Institute.

        **WARNING:** These tools are designed with **very** strong assumptions about data structure and formats, as well as available resources (e.g., file system, database). While bits and pieces of the code may be useful in other contexts, as a general rule, if you try to install/use this package somewhere other than one of a handful of properly configured BRI servers, *you're going to have a bad time*.

-----

Features
--------

Currently, there are three primary functions served by package modules:

- Generation of workflow instructions and submission of data processing batches
- Collection and organization of output data from bioinformatics processing workflows
- Annotation and import of pipeline input & output data into the Genomics Core Mongo database — i.e., **GenLIMS**

These features are continuing to expand and evolve over time.

Installation
------------

bripipetools can be installed by cloning this repository and running::

    $ pip install .

For development, the recommended setup is the following:

    $ conda env create -n bripipetools environment.yml
    $ source activate bripipetools
    $ pip install -e .

To test that the application was installed:

    $ python setup.py test  # for production
    $ py.test  # for development
    $ bripipetools --help

Documentation
-------------

The documentation for bripipetools is available `here <http://bripipelinetools.readthedocs.io/en/latest/?badge=latest>`_ (courtesy of `ReadTheDocs <http://readthedocs.org/>`_).

Contribute
----------

- Issue tracker: github.com/BenaroyaResearch/bripipetools/issues
- Source code: github.com/BenaroyaResearch/bripipetools/bripipetools

License
-------

The project is licensed under the MIT license.
