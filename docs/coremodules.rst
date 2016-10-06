bripipetools core modules
=========================

"Core" modules are where most of the heavy lifting happens, and are called by application-level modules to perform various pipeline tasks. Modules are listed roughly in order of dependency hierarchy (i.e., modules listed first depend on subsequently listed modules).

.. note:: **Intended for developers!**

    The documentation below is effectively a dump of all low-level modules, submodules, classes, and methods that are used to run bripipetools. This amount of detail shouldn't be needed for most users, but provides a starting point for those looking to understand or modify the code.

-----

``annotation`` module
---------------------

.. automodule:: bripipetools.annotation

-------------------------
``illuminaseq`` submodule
-------------------------

.. automodule:: bripipetools.annotation.illuminaseq

--------------------------
``globusgalaxy`` submodule
--------------------------

.. automodule:: bripipetools.annotation.globusgalaxy

-----

``qc`` module
-------------

.. automodule:: bripipetools.qc

----------------------
``sexcheck`` submodule
----------------------

.. automodule:: bripipetools.qc.sexcheck

-----

``genlims`` module
------------------

.. automodule:: bripipetools.genlims

------------------------
``connection`` submodule
------------------------

.. automodule:: bripipetools.genlims.connection

------------------------
``operations`` submodule
------------------------

.. automodule:: bripipetools.genlims.operations

---------------------
``mapping`` submodule
---------------------

.. automodule:: bripipetools.genlims.mapping

-----

``model`` module
----------------

.. automodule:: bripipetools.model

-----------------------
``documents`` submodule
-----------------------

.. automodule:: bripipetools.model.documents

-----

``io`` module
-------------

.. automodule:: bripipetools.io

---------------------------
``workflowbatch`` submodule
---------------------------

.. automodule:: bripipetools.io.workflowbatch

---------------------------
``picardmetrics`` submodule
---------------------------

.. automodule:: bripipetools.io.picardmetrics

--------------------------
``htseqmetrics`` submodule
--------------------------

.. automodule:: bripipetools.io.htseqmetrics

-------------------------
``tophatstats`` submodule
-------------------------

.. automodule:: bripipetools.io.tophatstats

---------------------
``fastqc`` submodule
---------------------

.. automodule:: bripipetools.io.fastqc

-------------------------
``htseqcounts`` submodule
-------------------------

.. automodule:: bripipetools.io.htseqcounts

-----

``parsing`` module
------------------

.. automodule:: bripipetools.parsing

----------------------
``illumina`` submodule
----------------------

.. automodule:: bripipetools.parsing.illumina

-----

``util`` module
---------------

.. automodule:: bripipetools.util

---------------------
``strings`` submodule
---------------------

.. automodule:: bripipetools.util.strings

-------------------
``files`` submodule
-------------------

.. automodule:: bripipetools.util.files
