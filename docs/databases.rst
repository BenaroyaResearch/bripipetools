.. _databases-page:

*********
Databases
*********

There are two databases which are important to consider in the context of the BRI genomics pipeline. These databases are called **GenLIMS** and the **Research Database**.

.. _genlims-intro:

GenLIMS
=======

GenLIMS ("General Laboratory Information Management System") is the primary sample tracking system for the Genomics Core. GenLIMS is built on the same MongoDB architecture as the **BRI Sample Repository** and **Research Database** (see Charlie Quinn of the Data Management and Software Development Core for details). What began as a sample tracking system named **TG2** at Baylor University evolved into **TG3** to address information management needs that were increasingly beyond the scope of microarray and qPCR experiments. **GenLIMS is the primary location for sequencing library ID generation and storage.** In this way the data that are processed by bripipetools are connected back to GenLIMS, but bripipetools does not interact with GenLIMS directly.

While the underlying MongoDB database is still technically named ``tg3``, the system and interface are now referred to as GenLIMS.

GenLIMS Servers
---------------

Accessing the GenLIMS servers requires access to the BRI network, either on-site or via VPN. The production instance of GenLIMS is hosted at ``srvgenlims01.brivmrc.org``. A test instance of the database also exists at ``srvsdb11.brivmrc.org``. For development purposes, testing with a local copy of ``srvgenlims01`` works well. Please contact the Bioinformatics or Software Development groups at BRI for database user and password information.

.. _resdb-intro:

The Research Database
=====================

The goal of the BRI Research Database is to connect all available information about any sample that's been analyzed in any way at BRI. This helps speed analyses, improve reproducibility, and identify errors in data. **The Research Database is the primary location for sequencing data and annotation storage.** The bripipetools programs interact directly with the Research Database at a number of levels. When there are discrepancies between annotations, the information in the Sample Repository is treated as "ground truth".

The underlying MongoDB database for the Research Database is currently named ``bri``.

Research Database Servers
-------------------------

Accessing the Research Database servers requires access to the BRI network, either on-site or via VPN. The production instance of the Research Database is hosted at ``srvmongo01.brivmrc.org``. A test instance of the database also exists at ``srvsdb11.brivmrc.org``. For development purposes, testing with a local copy of ``srvmongo01`` is possible, but in many cases testing against the staging server is preferred (see warning about database copy sizes below). Please contact the Bioinformatics or Software Development groups at BRI for database user and password information.

.. _databases-infra:

Infrastructure & Setup
======================

Documents
---------

Individual elements in the database are represented by **documents**. These are also commonly referred to as **objects**. A document in MongoDB is simply a map of key-value pairs, very much like dictionaries in Python.

Collections
-----------

Collections represent fundamental abstractions of physical objects, procedures, and data objects within the Genomics and Bioinformatics groups. One of the key advantages of managing data within a NoSQL database is the flexibility to handle new data types, without needing to fit within a rigid schema. As such, the list of collections and object types below are likely to expand over time. 

As described below, bripipetools interacts with collections the Research Database, but data in these collections may contain references to documents in GenLIMS. There are also collections in the Research Database which are not accessed by bripipetools. These collections may contain information relevant to samples processed by bripipetools, but will not be discussed in detail here. To designate collections that are accessed by or relevant to bripipetools, a prefix of "genomics" is used in the collection name.

Setting up a Local Database Copy
--------------------------------

.. warning:: **Database Copy Size**

    Before you begin the following steps, it's important to realize that database copies can take up a significant amount of hard drive space. Currently the Research Database occupies ~50 Gb on disk. To dump specific collections, you can use the ``-c`` argument to ``mongodump``

The steps below assume that you already have **MongoDB** installed on your machine. If not, you can find download and install instructions `here <https://www.mongodb.com/download-center#community>`_. Note: ``bripipetools`` has been tested with version ``3.2`` of MongoDB.

Note: Please contact the Bioinformatics or Software Development groups at BRI for database user and password information.

Setup ``data/db`` directory:

.. code-block:: sh

    cd / # or wherever you'd like to store your databases
    sudo mkdir data
    sudo chmod a+rwx data
    cd data
    mkdir db
    mongod # this must be left running in background or different shell

Connect to ``admin``:

.. code-block:: sh

    mongo admin

Set up ``bri`` (or ``tg3``):

.. code-block:: mongo

    use bri
    db.createUser({user:"<user>",pwd:"<password>",roles:["readWrite","dbAdmin"]})
    quit()

Connect to ``bri``:

.. code-block:: sh

    mongo -u <user> -p <password> bri


Test ``bri``::

    show collections;
    quit()


Copy database into ``jnk/dump`` (see warning above about database sizes):

.. code-block:: sh

    cd
    mkdir jnk
    cd jnk
    # retrieve a copy of the database using mongodump
    mongodump -u <user> -p <password> --host srvmongo01 -d bri
    cd dump
    # restore a database to your local mongo instance (host default is localhost)
    # BE CAREFUL IF YOU MODIFY THIS COMMAND:
    # the `--drop` option will drop the existing database before loading.
    mongorestore -u <user> -p <password> --drop -d bri bri


.. _resdb-collections:

Research Database Collections
=============================

genomicsAccess
--------------

This collection contains information about which user accounts and groups are allowed to access project data. Although this collection is not directly accessed by bripipetools currently, this collection is used to restrict or permit access to processed data through the `Bioinformatics Analysis Portal <http://www.bap.benaroyaresearch.org/>`_.

genomicsAnnotations
-------------------

Each document in the annotations collection contains various annotation information and metadata for a single library. Each document is assumed to have, at minimum: 

* A field ``project``, containing a project ID of the form *P{projectNumber}-{subprojectNumber}*
* A field ``libid``, containing a library ID of the form *lib{libraryNumber}*
* A field ``sampleId``. This should ideally contain the GenLIMS sample ID of the form *S{sampleNumber}*, but some records may have other values here (see note on data import below).
* A field ``sampleName``, containing an arbitrary sample name

Note: Data for this collection largely come from spreadsheets that are shared between multiple different researchers during the experiment planning phase. There are a number of ongoing efforts to improve the consistency and accuracy of data in this collection, but mistakes do happen, and currently not all records have consistent conventions. If you identify a sample annotation issue, please contact Mario Rosasco for assistance.

genomicsCounts
--------------

Counts documents contain raw gene count data, generally from an RNAseq sequencing experiment. 

.. warning:: **Number of Fields Per Document**
    
    Note that each document in this collection contains a field, ``geneCounts``, which contains a subdocument with a field for each gene in the reference genome. Depending on the genome used, this means there are likely tens of thousands of fields for each document in the collection. As you browse data, be aware of this fact; trying to load multiple documents from this collection can cause slowdown of your computer while the mongo client tries to render the large documents.

.. _databases-metrics:

genomicsMetrics
---------------

The various metrics generated by workflows are collected and inserted into this collection. There are a number of fields which may or may not be present, depending on the sort of experiment that was run, but for a standard RNAseq experiment (the most common), alignment metric fields commonly used for quality control include:

* ``picardRnaseq.medianCvCoverage`` - the median CV of gene model coverage for the top-expressed genes
* ``tophatStats.fastqTotalReads`` - the total number of reads (ie: "depth") in the input fastq file
* ``picardMarkdups.unpairedReadsExamined`` - the number of reads that were aligned as singletons
* ``picardMarkdups.pairedReadsExamined`` - the number of reads that were aligned in pairs

.. _databases-runs:

genomicsRuns
------------

Each document in this collection corresponds to a "run" - ie: a sequencing flow cell. The instrument number, date, ID, and position on the sequencer are stored to help keep track of each run.

.. _databases-samples:

genomicsSamples
---------------

From the perspective of bripipetools, a sample is synonymous with a library. Documents in this collection correspond to documents with type ``sequenced library`` or ``processed library`` in the GenLIMS ``samples`` collection. Samples are connected by the ``parentId`` field, where a sample's parent was "converted" to the current sample through some **protocol**.

Any sample, regardless of type or source, is added to the GenLIMS ``samples`` collection as type ``sample`` with an S-ID (e.g., ``S0001``). If a sample is received as whole blood or some other sample storage related specimen, its source protocol is marked as ``incoming``. If a sample is received as some other Genomics Core assay type (e.g., ``library``), then it is also cloned and added as a sample document of that type.

The imaginary point at which samples cross from the Genomics Core domain to Bioinformatics is ``library`` to ``sequenced library`` — while everything up to and including ``library`` represents a physical specimen, a ``sequenced library`` points to a FASTQ file generated by the sequencing process. The results of bioinformatics processing performed on a ``sequenced library`` sample are stored in a ``processed library`` document.

.. _databases-tcr:

genomicsTCR
-----------

Each of the documents in ``genomicsTCR`` represents one TCR or BCR chain that was identified in one library. This is usually the result of running Trinity and MiXCR on single-cell or clonal RNAseq libraries. Each document includes the full nucleotide seqeunce for the coding region, the amino acid sequence of the junction/CDR3 region, and various metadata about the quality of the gene matching and the version of the tools used.

.. _databases-batches:

genomicsWorkflowbatches
-----------------------

This collection stores information about how projects on a flow cell were processed through a workflow on Galaxy. Each document corresponds to one batch file, associated with one workflow and one or more projects. Any available version information about tools accessed by the workflow is stored in each document, to help track changes and updates that will happen to workflows over time. A ``processed library`` document in the ``samples`` collection stores the results of one library processed as part of a workflow batch.



-----



.. _genlims-collections:

GenLIMS Collections
===================

Although bripipetools now relies entirely on the Research Database and no longer directly interacts GenLIMS, older versions of bripipetools had a closer connection to GenLIMS. Sample IDs should connect the data between the two databases to help trace back sample processing steps. For this reason, the following description of GenLIMS collections has been copied for reference/completeness.

Collections
-----------

Collections represent fundamental abstractions of both physical objects, procedures, and data objects within the Genomics and Bioinformatics Cores. One of the key advantages of managing data within a NoSQL database is the flexibility to handle new data types, without needing to fit within a rigid schema. As such, the list of collections and object types below are likely to expand over time.

samples
^^^^^^^

Samples, in a nutshell, are the data. Documents in this collection represent either physical or digital specimens, derived in some way from a subject or animal. Sample types correspond to their stage in either experimental or bioinformatics processing (e.g., ``tRNA`` for total RNA, ``grRNA`` for globin-reduced RNA, or ``library`` for sequencing library). Samples are connected by the ``parentId`` field, where a sample's parent was "converted" to the current sample through some **protocol**.

Any sample, regardless of type or source, is added to the ``samples`` collection as type ``sample`` with an S-ID (e.g., ``S0001``). If a sample is received as whole blood or some other sample storage related specimen, its source protocol is marked as ``incoming``. If a sample is received as some other Genomics Core assay type (e.g., ``library``), then it is also cloned and added as a sample document of that type.

The imaginary point at which samples cross from the Genomics Core domain to Bioinformatics core is ``library`` to ``sequenced library`` — while everything up to and including ``library`` represents a physical specimen, a ``sequenced library`` points to a FASTQ file generated by the sequencing process. The results of bioinformatics processing performed on a ``sequenced library`` sample are stored in a ``processed library`` document.


batches
^^^^^^^

I'm not entirely sure what the ``batches`` collection represents. You'll have to ask Charlie.

projects
^^^^^^^^

Projects represent individual studies, and subprojects typically correspond to specific experiments performed within these studies. Thus, the basic unit under which samples are grouped is a project and subproject. This grouping is typically labelled with a P-ID (e.g., ``P1-2`` for project 1, subproject 2).

protocols
^^^^^^^^^

Again, protocols are the processes by which samples are interconverted from one type to another. For more information, refer to the :ref:`genomics-protocols` section of the genomics data page.

runs
^^^^

Runs represent uniquely identifiable instantiations of protocols. For example, a ``flowcell run`` would be linked to the ``sequencing`` protocol and have an ID corresponding to the flowcell ID (other examples include C1 plates and qPCR chips).

workflows
^^^^^^^^^

The ``workflows`` collection strictly pertains to the Bioinformatics Core side of the pipeline. Documents in this collection describe the steps and tools comprising data processing workflows (typically in Galaxy or Globus Galaxy).

workflowbatches
^^^^^^^^^^^^^^^

Workflow batches are perhaps the most important element of bioinformatics processing, encompassing all samples (sequenced libraries) processed together with a particular workflow. 



-----


