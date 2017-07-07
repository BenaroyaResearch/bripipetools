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
* bioinformatics processing [PROPOSED]

-----


.. _genomics-storage:

Data storage
============

(sea-zed-01, Chaussabel lab share)



Genomics share
--------------

The 'genomics' share is the primary location at which data (sequencing or otherwise) is stored. A variety of other data files and code related to processing are also stored under the 'genomics' share, but raw data is nominally stored in one of several subfolders according to source. These are described as "landing points" below.


Basic landing points
^^^^^^^^^^^^^^^^^^^^

* ``Illumina`` (``/mnt/genomics/Illumina/``)
* ``SRA`` (``/mnt/genomics/SRA/``)
* ``ICAC`` (``/mnt/genomics/ICAC/``)
* ``NGXBio`` (``/mnt/genomics/NGXBio/``)
* ``Fluidigm`` (``/mnt/genomics/Fluidigm/``)


Reference data
^^^^^^^^^^^^^^

``/mnt/genomics/reference_data/``

* ``annotationsForGalaxy``
* ``Genomes``
* ``iGenomes``
* ``ERCC92``


Special folders
^^^^^^^^^^^^^^^

* ``code`` (``/mnt/genomics/code/``)
* ``galaxy_workflows`` (``/mnt/genomics/galaxy_workflows/``)
* ``geo_submissions`` (``/mnt/genomics/geo_submissions/``)


Old Galaxy data
^^^^^^^^^^^^^^^

* ``srvgalaxy02``


Chaussabel lab share
--------------------

Projects

Flowcell log
