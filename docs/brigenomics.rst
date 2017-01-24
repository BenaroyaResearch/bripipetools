.. _genomics-page:

*****************
BRI Genomics Data
*****************

The vast majority of data handled by the Bioinformatics Core — and by extension, with **bripipetools** — are generated in the Genomics Core (contact: Vivian Gersuk). Furthermore, most samples that pass through the Genomics Core originate in the BRI Sample Repository (notable exceptions include samples from large grants or studies such as ICAC or ITN).

.. _genomics-protocols:

Protocols
=========

Operations related to experimental processing and data generation of Genomics Core samples are generally described by **protocols** (see the :ref:`genlims-page` page). Protocols are classified by type, indicating the overall goal or purpose of a procedure or series of steps. A **run** represents an identifiable instance of a protocol, typically corresponding to a specific chip, plate, or flowcell. Current protocols and associated run types are listed below.

* incoming
* RNA extraction
* miRNA extraction
* RNA purification
* globin reduction
* cell capture
* cDNA synthesis
* library prep
* custom library prep
* sequencing
* qPCR
* bioinformatics processing

.. _genomics-storage:

Data storage
============

(sea-zed-01, Chaussabel lab share)



Genomics share
--------------

Basic org::

    Unaligned/
    |--P123-7-31993980/
        |--lib12829-38905932/
        |--1-SLE-C36_S153_L007_R1_001.fastq.gz


Basic landing points
^^^^^^^^^^^^^^^^^^^^

* ``Illumina``
* ``SRA``
* ``ICAC``
* ``NGXBio``
* ``Fluidigm``


Reference data
^^^^^^^^^^^^^^

* ``annotationsForGalaxy``
* ``Genomes``
* ``iGenomes``
* ``ERCC92``


Special folders
^^^^^^^^^^^^^^^

* ``code``
* ``galaxy_workflows``
* ``geo_submissions``


Old Galaxy data
^^^^^^^^^^^^^^^

* ``srvgalaxy02``


Chaussabel lab share
--------------------

Projects

Flowcell log
