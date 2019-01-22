**************************
bripipetools core packages
**************************

Overview
========

"Core" packages are where most of the heavy lifting happens, and are called by application-level modules to perform various pipeline tasks. Packages are listed roughly in order of dependency hierarchy (i.e., packages listed first depend on subsequently listed packages).

.. note:: **Intended for developers!**

    The documentation below is effectively a dump of all low-level packages, modules, classes, and methods that are used to run bripipetools. This amount of detail shouldn't be needed for most users, but provides a starting point for those looking to understand or modify the code.

-----

Package details
===============

``annotation`` package
----------------------

.. automodule:: bripipetools.annotation

``sequencedlibraries`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.annotation.sequencedlibs

``flowcellruns`` module
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.annotation.flowcellruns

``processedlibraries`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.annotation.processedlibs


``workflowbatches`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.annotation.workflowbatches

-----

``qc`` package
--------------

.. automodule:: bripipetools.qc

``sexcheck`` module
^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.qc.sexcheck

``sexverify`` module
^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.qc.sexverify

``sexpredict`` module
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.qc.sexpredict

-----

``database`` package
--------------------

.. automodule:: bripipetools.database

``connection`` module
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.database.connection

``operations`` module
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.database.operations

``mapping`` module
^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.database.mapping

-----

``model`` package
-----------------

.. automodule:: bripipetools.model

``documents`` module
^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.model.documents

-----

``io`` package
--------------

.. automodule:: bripipetools.io

``workflow`` module
^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.workflow

``workflowbatch`` module
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.workflowbatch

``picardmetrics`` module
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.picardmetrics

``htseqmetrics`` module
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.htseqmetrics

``tophatstats`` module
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.tophatstats

``fastqc`` module
^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.fastqc

``htseqcounts`` module
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.htseqcounts

``sexcheck`` module
^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.io.sexcheck

-----

``parsing`` package
-------------------

.. automodule:: bripipetools.parsing

``gencore`` module
^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.parsing.gencore

``illumina`` module
^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.parsing.illumina

``processing`` module
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.parsing.processing

-----

``util`` module
---------------

.. automodule:: bripipetools.util

``strings`` submodule
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.util.strings

``files`` submodule
^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.util.files
