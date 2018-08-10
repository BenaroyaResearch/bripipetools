.. _genlims-page:

*******
GenLIMS
*******

The core component of genomics data processing pipelines at BRI — in spirit, at least, and increasingly in practice — is the GenLIMS database. GenLIMS is built on the same MongoDB architecture as the **BRI Sample Repository** and **Research Database** (see Charlie Quinn of the Data Management and Software Development Core for details). What began as a sample tracking system named **TG2** at Baylor University evolved into **TG3** to address information management needs that were increasingly beyond the scope of microarray and qPCR experiments.

While the underlying MongoDB database is still technically named ``tg3``, the system and interface are now referred to as GenLIMS.

.. _genlims-infra:

Infrastructure & Setup
======================

Servers
-------

The production instance of GenLIMS/TG3 is hosted at ``srvtg301.brivmrc.org``, which is accessible on site at BRI or through a VPN connection. A test instance of the database also exists at ``srvt03.brivmrc.org``. For development purposes, testing with a local copy of ``srvtg301`` works well. User and password information for both production and test versions of the database are stored on Box in the ``bripipetools-config`` folder.


Setting up TG3
--------------

The steps below assume that you already have **MongoDB** installed on your machine. If not, you can find download and install instructions `here <https://www.mongodb.com/download-center#community>`_. Note: ``bripipetools`` has been tested with version ``3.2`` of MongoDB.

Note: user and password information are stored in private INI config files on Box.

Setup ``data/db`` directory::

    cd /
    sudo mkdir data
    sudo chmod a+rwx data
    cd data
    mkdir db
    mongod

Connect to ``admin``::

    mongo admin

Set up ``tg3``::

    use tg3
    switched to db tg3
    db.createUser({user:"<user>",pwd:"<password>",roles:["readWrite","dbAdmin"]})
    Successfully added user: { "user" : "<user>", "roles" : [ "readWrite", "dbAdmin" ] }
    quit()

Connect to ``tg3``::

    mongo -u <user> -p <password> tg3


Test ``tg3``::

    show collections;
    quit()


Set up ``jnk/dump``::

    cd
    mkdir jnk
    cd jnk
    mongodump -u <user> -p <password> --host srvtg301 -d tg3
    cd dump
    mongorestore -u <user> -p <password> --drop -d tg3 tg3


Perform mongo 'pull' (dump + restore)::

    cd $HOME
    rm -rf dump/dc
    mongodump -u <user> -p <password> --host srvtg301 -d tg3
    cd dump/tg3
    rm logging*
    rm system.*
    cd ..
    mongorestore --drop -d tg3 tg3


-----


.. _genlims-architect:

Architecture
============

For details regarding design decisions and application code for managing GenLIMS, refer to Charlie Quinn. At a high level, GenLIMS is organized according to the basic principals of a NoSQL database like MongoDB.

Documents
---------

Individual elements in the database are represented by documents. These are also commonly referred to as **objects**, but to avoid confusion with Python objects in the **bripipetools** codebase, we'll stick with documents here. A document in MongoDB is simply a map of key-value pairs, very much like dictionaries in Python.


Collections
-----------

Collections represent fundamental abstractions of both physical objects, procedures, and data objects within the Genomics and Bioinformatics Cores. One of the key advantages of managing data within a NoSQL database is the flexibility to handle new data types, without needing to fit within a rigid schema. As such, the list of collections and object types below are likely to expand over time.

To ease navigation and provide some context, both collections and object types are tagged according to which end of the experimental/computational spectrum they pertain.

samples
^^^^^^^

[GenCore, BfxCore]

Samples, in a nutshell, are the data. Documents in this collection represent either physical or digital specimens, derived in some way from a subject or animal. Sample types correspond to their stage in either experimental or bioinformatics processing (e.g., ``tRNA`` for total RNA, ``grRNA`` for globin-reduced RNA, or ``library`` for sequencing library). Samples are connected by the ``parentId`` field, where a sample's parent was "converted" to the current sample through some **protocol**.

Any sample, regardless of type or source, is added to the ``samples`` collection as type ``sample`` with an S-ID (e.g., ``S0001``). If a sample is received as whole blood or some other sample storage related specimen, its source protocol is marked as ``incoming``. If a sample is received as some other Genomics Core assay type (e.g., ``library``), then it is also cloned and added as a sample document of that type.

The imaginary point at which samples cross from the Genomics Core domain to Bioinformatics core is ``library`` to ``sequenced library`` — while everything up to and including ``library`` represents a physical specimen, a ``sequenced library`` points to a FASTQ file generated by the sequencing process. The results of bioinformatics processing performed on a ``sequenced library`` sample are stored in a ``processed library`` document.


batches
^^^^^^^

[GenCore]

I'm not entirely sure what the ``batches`` collection represents. You'll have to ask Charlie.

projects
^^^^^^^^

[GenCore]

Projects represent individual studies, and subprojects typically correspond to specific experiments performed within these studies. Thus, the basic unit under which samples are grouped is a project and subproject. This grouping is typically labelled with a P-ID (e.g., ``P1-2`` for project 1, subproject 2).

protocols
^^^^^^^^^

[GenCore, BfxCore]

Again, protocols are the processes by which samples are interconverted from one type to another. For more information, refer to the :ref:`genomics-protocols` section of the genomics data page.

runs
^^^^

[GenCore]

Runs represent uniquely identifiable instantiations of protocols. For example, a ``flowcell run`` would be linked to the ``sequencing`` protocol and have an ID corresponding to the flowcell ID (other examples include C1 plates and qPCR chips).

workflows
^^^^^^^^^

[BfxCore]

The ``workflows`` collection strictly pertains to the Bioinformatics Core side of the pipeline. Documents in this collection describe the steps and tools comprising data processing workflows (typically in Galaxy or Globus Galaxy).

workflowbatches
^^^^^^^^^^^^^^^

[BfxCore]

Workflow batches are perhaps the most important element of bioinformatics processing, encompassing all samples (sequenced libraries) processed together with a particular workflow. A ``processed library`` document in the ``samples`` collection stores the results of one or more workflow batches.
