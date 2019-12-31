.. _genomics-page:

*****************
BRI Genomics Data
*****************

The vast majority of data handled by the Bioinformatics Core — and by extension, with **bripipetools** — are generated in the Genomics Core (contact: Vivian Gersuk). Furthermore, most samples that pass through the Genomics Core originate in the BRI Sample Repository (notable exceptions include samples from large grants or studies such as ICAC or ITN).

.. _genomics-protocols:

Protocols
=========

Operations related to experimental processing and data generation of Genomics Core samples are generally described by **protocols** and are tracked in GenLIMS (see the :ref:`databases-page` page). Protocols are classified by type, indicating the overall goal or purpose of a procedure or series of steps. A **run** represents an identifiable instance of a protocol, typically corresponding to a specific chip, plate, or flow cell. Current protocols and associated run types are listed below.

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

(isilon, Chaussabel lab share)

Isilon
------
In 2019, BRI set up the primary storage server for genomics (and other data) to be ``isilon.brivmrc.org`` to replace ``sea-zed-01.brivmrc.org``.


Genomics/Bioinformatics shares
------------------------------

**NB** - Following the implementation of isilon at BRI, the primary data from the sequencing machine (.bcl image files) were separated from the processed data (.fastq sequences and further downstream files) in order to aid in improving disaster recovery efforts by IT. The former (raw data) are stored in the ``/genomics/`` share on Isilon, and should not need to be accessed during normal operations. The processed data (sequencing and otherwise) are stored in the ``/bioinformatics`` share region  of Isilon. A variety of other data files and code related to processing are also stored under the ``/bioinformatics/`` share, but data are nominally stored in one of several subfolders according to source. These are described as "landing points" below.


Basic landing points
^^^^^^^^^^^^^^^^^^^^

* ``Illumina`` (``/mnt/bioinformatics/pipeline/Illumina/``)
* ``Annotations`` (``/mnt/bioinformatics/pipeline/annotation/)
* ``SRA`` (``/mnt/bioinformatics/workspace/SRA/``)
* ``ICAC`` (``/mnt/bioinformatics/workspace/ICAC/``)
* ``NGXBio`` (``/mnt/bioinformatics/workspace/NGXBio/``)
* ``Fluidigm`` (``/mnt/bioinformatics/workspace/Fluidigm/``)


Reference data
^^^^^^^^^^^^^^

``/mnt/bioinformatics/workspace/reference_data/``

* ``annotationsForGalaxy``
* ``Genomes``
* ``iGenomes``
* ``ERCC92``


Special folders
^^^^^^^^^^^^^^^

* ``code`` (``/mnt/bioinformatics/workspace/code/``)
* ``galaxy_workflows`` (``/mnt/bioinformatics/pipeline/galaxy_workflows/``)
* ``geo_submissions`` (``/mnt/bioinformatics/workspace/geo_submissions/``)


Old Galaxy data
^^^^^^^^^^^^^^^

* ``/mnt/bioinformatics/pipeline/Archive``


Project tracking database
-------------------------

`GCQ (Genomics Core Queue) <https://gcq.benaroyaresearch.org/>_` 

Chaussabel lab share
--------------------

* Main lab share: ``srvstor01/DFS_Chaussabel_LabShare``
* Flowcell log: ``srvstor01/DFS_Chaussabel_LabShare/Illumina HiScan SQ/Flowcell log.xlsx``
