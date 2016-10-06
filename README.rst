
.. image:: https://img.shields.io/travis/jaeddy/bripipetools.svg
        :target: https://travis-ci.org/jaeddy/bripipetools

.. image:: https://img.shields.io/coveralls/jaeddy/bripipetools.svg
        :target: https://coveralls.io/github/jaeddy/bripipetools

.. image:: https://readthedocs.org/projects/bripipetools/badge/?version=latest
        :target: http://bripipetools.readthedocs.io/en/latest/?badge=latest


bripipetools
============

**bripipetools** (i.e., BRI Pipeline Tools) is a collection of modules for managing the operation of processing workflows — as well as the input and output data for these workflows — within the Genomics and Bioinformatics Cores at the Benaroya Research Institute.

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

Documentation
-------------

The documentation for bripipetools is available `here <https://readthedocs.org/projects/bripipetools/badge/?version=latest>`_ (courtesy of `ReadTheDocs <http://readthedocs.org/>`_).

Contribute
----------

- Issue tracker: github.com/jaeddy/bripipetools/issues
- Source code: github.com/jaeddy/bripipetools

License
-------

The project is licensed under the MIT license.
