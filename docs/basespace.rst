.. _basespace-page:

*********
BaseSpace
*********

.. _basespace-download:

Downloading data
================

The next step is to download project FASTQs from **BaseSpace**. You'll want to use a computer that will remain awake and connected to the internet for about an hour. Once Vivian has shared the completed projects with you on [**BaseSpace**](https://basespace.illumina.com/) (you'll need an account), you can go to your dashboard and accept each of the shared project invitations.

Next, go to the the **Projects** tab, and for each project on the flowcell, do the following:

1. Select the current project by clicking on the project name.
2. Hit the **Download Project** up top to download all samples for the project (you'll need the BaseSpace downloader app installed).

**Note:** In some cases, samples (libraries) under the same project ID will be run on multiple flowcells. When this happens, you need to select samples individually to only download the most recent batch:

1. Select project
2. Select all libraries on each page by checking the box at the top (repeat for each page of libraries — yes, you have to select 25 at a time)<sup>*</sup>
3. Hit the **Download Samples** button up top to download the selected samples
4. Select **Save** and choose to save data in the ``Unaligned/`` folder you created above (located on ``srvzfs01``). **BaseSpace** will automatically create a unique sub-folder for each project.

<sup>\* When selecting individually, BaseSpace allows up to 200 libraries to be selected for download at the same time; if a project/run contains more than 200 libraries, the download will need to be split up into multiple batches.</sup>

-----

.. _basespace-backup:

Backing up data
===============

``basemount``
-------------

Using ``backup_basespace.py``
-----------------------------

This script will backup data files from projects on BaseSpace to the directory ``/mnt/genomics/Illumina/basespace_backup``. For each project, logs and property data are copied to a subfolder corresponding to the flowcell ID (note: these data are the same for all projects on a flowcell, so if the subfolder already exists, the project will be skipped).

Organization::

    python basespace_backup.py \
	    /mnt/genomics/Illumina/basespace_mount \
    	/mnt/genomics/Illumina/basespace_backup

