bripipetools application modules
================================

Application-level modules are those exposed to the user through wrapper scripts and (ultimately) the command line. They are used to perform common, high-level tasks related to pipeline operations and data. Modules are listed roughly in order of dependency hierarchy (i.e., modules listed first depend on subsequently listed modules).

.. note:: **Intended for developers!**

    The documentation below is effectively a dump of all high-level modules, submodules, classes, and methods that are used to run bripipetools. This amount of detail shouldn't be needed for most users, but provides a starting point for those looking to understand or modify the code.

-----

``dbify`` module
----------------

.. automodule:: bripipetools.dbify

---------------------
``control`` submodule
---------------------

.. automodule:: bripipetools.dbify.control

------------------------
``sequencing`` submodule
------------------------

.. automodule:: bripipetools.dbify.sequencing

------------------------
``processing`` submodule
------------------------

.. automodule:: bripipetools.dbify.processing

-----

``postprocess`` module
----------------------

.. automodule:: bripipetools.postprocess

-----------------------
``stitching`` submodule
-----------------------

.. automodule:: bripipetools.postprocess.stitching

---------------------
``cleanup`` submodule
---------------------

.. automodule:: bripipetools.postprocess.cleanup
