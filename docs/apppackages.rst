bripipetools application modules
================================

Application-level packages are those exposed to the user through wrapper scripts and the command line. They are used to perform common, high-level tasks related to pipeline operations and data. Packages are listed roughly in order of dependency hierarchy (i.e., packages listed first depend on subsequently listed packages).

.. note:: **Intended for developers!**

    The documentation below is effectively a dump of all high-level packages, modules, classes, and methods that are used to run bripipetools. This amount of detail shouldn't be needed for most users, but provides a starting point for those looking to understand or modify the code.

-----

``dbify`` package
-----------------

.. automodule:: bripipetools.dbify

---------------------
``control`` submodule
---------------------

.. automodule:: bripipetools.dbify.control

----------------------
``flowcellrun`` module
----------------------

.. automodule:: bripipetools.dbify.flowcellrun

------------------------
``workflowbatch`` module
------------------------

.. automodule:: bripipetools.dbify.workflowbatch

-----

``postprocess`` package
-----------------------

.. automodule:: bripipetools.postprocess

--------------------
``stitching`` module
--------------------

.. automodule:: bripipetools.postprocess.stitching

--------------------
``compiling module``
--------------------

.. automodule:: bripipetools.postprocess.compiling

------------------
``cleanup`` module
------------------

.. automodule:: bripipetools.postprocess.cleanup

-----

``monitoring`` package
----------------------

.. automodule:: bripipetools.postprocess

--------------------------
``workflowbatches`` module
--------------------------

.. automodule:: bripipetools.postprocess.workflowbatches

-----

``submission`` package
----------------------

.. automodule:: bripipetools.submission

-------------------------
``flowcellsubmit`` module
-------------------------

.. automodule:: bripipetools.submission.flowcellsubmit

----------------------
``batchcreate`` module
----------------------

.. automodule:: bripipetools.submission.batchcreate

----------------------------
``batchparameterize`` module
----------------------------

.. automodule:: bripipetools.submission.batchparameterize
