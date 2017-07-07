.. _basespace-page:

*********
BaseSpace
*********

.. _basespace-download:

Downloading data
================

You'll want to use a computer that will remain awake and connected to the internet for about an hour. Once Vivian has shared the completed projects with you on `BaseSpace <https://basespace.illumina.com/>`_ (you'll need an account), you can go to your dashboard and accept each of the shared project invitations.

Next, go to the the **Projects** tab, and for each project on the flowcell, do the following:

1. Select the current project by clicking on the project name.
2. Hit the **Download Project** up top to download all samples for the project (you'll need the BaseSpace downloader app installed).

**Note:** In some cases, samples (libraries) under the same project ID will be run on multiple flowcells. When this happens, you need to select samples individually to only download the most recent batch:

1. Select project
2. Select all libraries on each page by checking the box at the top (repeat for each page of libraries — yes, you have to select 25 at a time):superscript:`*`
3. Hit the **Download Samples** button up top to download the selected samples
4. Select **Save** and choose to save data in the ``Unaligned/`` folder you created above (located on ``srvzfs01``). BaseSpace will automatically create a unique sub-folder for each project.

:superscript:`*` When selecting individually, BaseSpace seems to allow up to ~200 libraries to be selected for download at the same time; if a project/run contains more than 200 libraries, the download will need to be split up into multiple batches.

-----


.. _basespace-backup:

Backing up data
===============

The ``basemount`` tool can be used to access BaseSpace data through the command line and copy files to a local server.

``basemount``
-------------

`BaseMount <https://basemount.basespace.illumina.com/>`_ is a tool provided by Illumina that allows you to mount BaseSpace data as a file system through an API.

From ``srvgalaxy01``, to activate the mount point::

    basemount /mnt/genomics/Illumina/basespace_mount/

This gives access via the command line to all projects that have been shared by Vivian.

Using ``backup_basespace.py``
-----------------------------

This script will backup data files from projects on BaseSpace to the directory ``/mnt/genomics/Illumina/basespace_backup``. For each project, logs and property data are copied to a subfolder corresponding to the flowcell ID (note: these data are the same for all projects on a flowcell, so if the subfolder already exists, the project will be skipped).

::

    python basespace_backup.py \
	    /mnt/genomics/Illumina/basespace_mount \
    	/mnt/genomics/Illumina/basespace_backup


The following data will be backed up for each flowcell run::

    /mnt/genomics/Illumina/basespace_backup/BCAC6PANXX/
    ├── logs
    │   ├── AdapterTrimming.txt
    │   ├── CompletedJobInfo.xml
    │   ├── ConversionStats.xml
    │   ├── DemultiplexingStats.xml
    │   ├── DemuxSummaryF1L1.txt
    │   ├── DemuxSummaryF1L2.txt
    │   ├── DemuxSummaryF1L3.txt
    │   ├── DemuxSummaryF1L4.txt
    │   ├── DemuxSummaryF1L5.txt
    │   ├── DemuxSummaryF1L6.txt
    │   ├── DemuxSummaryF1L7.txt
    │   ├── DemuxSummaryF1L8.txt
    │   ├── FastqSummaryF1L1.txt
    │   ├── FastqSummaryF1L2.txt
    │   ├── FastqSummaryF1L3.txt
    │   ├── FastqSummaryF1L4.txt
    │   ├── FastqSummaryF1L5.txt
    │   ├── FastqSummaryF1L6.txt
    │   ├── FastqSummaryF1L7.txt
    │   ├── FastqSummaryF1L8.txt
    │   ├── IndexMetricsOut.bin
    │   ├── Logging.zip
    │   ├── Reports.zip
    │   ├── RunInfo.xml
    │   ├── SampleSheetUsed.csv
    │   ├── WorkflowError.txt
    │   ├── WorkflowLog.txt
    │   ├── _metadata.json
    │   ├── bsfs-20170120041732604.log
    │   ├── output-20170120033226718.log
    │   ├── spacedock-20170120041731775.log
    │   ├── spacedock-infrastructure-20170120041731974.log
    │   └── uploader-20170120041732487.log
    └── properties
        ├── BaseSpace.Private.IsMultiNode
        ├── Input.Runs
        ├── Input.app-session-name
        ├── Input.run-id.attributes
        │   └── 0
        │       ├── FieldId
        │       ├── ResourceHref
        │       ├── ResourceId
        │       └── ResourceType
        ├── Input.sample-sheet
        ├── Logs.Tail
        ├── Output.Projects
        └── Output.Samples

This data is accessed once per flowcell at a project path like this::

    /mnt/genomics/Illumina/basespace_mount/Projects/P123-13/AppSessions/
    └── FASTQ Generation 2017-01-20 02:14:43Z
        ├── Logs
        ├── Logs.metadata
        └── Properties
