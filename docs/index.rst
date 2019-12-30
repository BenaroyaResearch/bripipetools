.. bripipetools documentation master file, created by
   sphinx-quickstart on Wed Oct  5 15:02:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

bripipetools
============

**bripipetools** (i.e., BRI Pipeline Tools) is a collection of packages for managing the operation of processing workflows — as well as the input and output data for these workflows — within the Genomics and Bioinformatics Cores at the Benaroya Research Institute.

.. warning:: **Scope & environment**

   These tools are designed with **very** strong assumptions about data structure and formats, as well as available resources (e.g., file system, database). While bits and pieces of the code may be useful in other contexts, as a general rule, if you try to install/use this package somewhere other than one of a handful of properly configured BRI servers, *you're going to have a bad time*.

-----

Contents:

.. toctree::
   :maxdepth: 1

   getstarted.rst
   databases.rst
   rnaseqprocessing.rst
   processing.rst
   postprocessing.rst
   brigenomics.rst
   basespace.rst
   galaxy.rst
   refdata.rst
   contributing.rst
   apppackages.rst
   corepackages.rst

-----

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
