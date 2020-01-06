*********************************
bripipetools Application Packages
*********************************

Overview
========

Application-level packages are those exposed to the user through wrapper scripts and the command line. They are used to perform common, high-level tasks related to pipeline operations and data. Packages are listed roughly in order of dependency hierarchy (i.e., packages listed first depend on subsequently listed packages).

.. note:: **Intended for developers!**

    The documentation below is effectively a dump of all high-level packages, modules, classes, and methods that are used to run bripipetools. This amount of detail shouldn't be needed for most users, but provides a starting point for those looking to understand or modify the code.

-----

Package details
===============

``dbification`` package
-----------------------

.. automodule:: bripipetools.dbification

``control`` submodule
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.dbification.control

``flowcellrun`` module
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.dbification.flowcellrun

``workflowbatch`` module
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.dbification.workflowbatch

-----

``postprocessing`` package
--------------------------

.. automodule:: bripipetools.postprocessing

``stitching`` module
^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.postprocessing.stitching

``compiling module``
^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.postprocessing.compiling

``cleanup`` module
^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.postprocessing.cleanup

-----

``monitoring`` package
----------------------

.. automodule:: bripipetools.monitoring

``workflowbatches`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.monitoring.workflowbatches

-----

``submission`` package
----------------------

.. automodule:: bripipetools.submission

``flowcellsubmit`` module
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.submission.flowcellsubmit

``samplesubmit`` module
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.submission.samplesubmit

``batchcreate`` module
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.submission.batchcreate

``batchparameterize`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: bripipetools.submission.batchparameterize
