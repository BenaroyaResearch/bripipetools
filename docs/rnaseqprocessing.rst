.. _rnaseqproc-page:

****************************
RNAseq Processing Quickstart
****************************

.. _rnaseqproc-intro:

Introduction
============

This page summarizes the steps that must be completed to process a flow cell's worth of RNAseq data. All of these steps assume that you have installed ``bripipetools`` according to the instructions at :ref:`start-install`

.. _rnaseqproc-getdata:

Retrieving Data
===============

*Before you begin:* Make sure that you have an Illumina BaseSpace account at `<http://basespace.illumina.com/>`_. Note that the following download can take up to a few hours, depending on the amount of data being retrieved.

1. The Genomics Core will send an email link to share access to the **run** and **projects**. You must accept all shares using the BaseSpace dashboard.
2. After accepting all shares and confirming the sequencing run is finished, go to your BaseSpace dashboard and click "RUNS" (top of the page), then the name of the run you want to download, then "Download" in the "SUMMARY" tab.
3. A popup will prompt you to download the data. If you haven't already installed the BaseSpace Sequence Hub Downloader do so, then select "FASTQ" as the file type to be downloaded, and click the "Download" button.
4. Save the FASTQ files to a directory called ``Unaligned`` within the flow cell directory. The exact path will differ depending on how you have the Bioinformatics directory mounted, but eg: on a Linux server the path will be ``/mnt/bioinformatics/pipeline/Illumina/{FlowcellID}/Unaligned``

Preprocessing Data
==================

.. warning:: **FASTQ Directory Structure**

   Starting in October 2017, the directory structure used by BaseSpace to store FASTQs changed slightly. As a result, the following script **must** be run in order to set up the directory structure for workflow processing. If the script is not run there will be no warning or indication of failure, but only one lane's worth of data will be processed for each project. If you see many fewer counts than expected, make sure that this step was done properly!

:: sh

    bripipetools/scripts/fix_fastq_paths.sh /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}    

Creating Workflow Batch Files
=============================

*Before you begin:* Make sure that the database configuration in ``bripipetools/bripipetools/config/default.ini`` is correct. There should be a config entry for ``[researchdb]`` with appropriately-set fields ``db_name``, ``db_host``, ``user``, and ``password``. If you have questions about the appropriate values to use, please contact Mario Rosasco.

1. Activate the ``bripipetools`` environment :: sh

    source activate bripipetools

2. Create a batch submission file. If you need to select non-standard workflows, you may want to look at the ``--workflow-dir`` and ``--all-workflows`` options. :: sh
    
    bripipetools submit /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}