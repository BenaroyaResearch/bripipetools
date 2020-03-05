.. _gotchas-page:

**********************************
Common Gotchas and Troubleshooting
**********************************

=======================
Globus Batch Submission
=======================

*Problem:* Only the first job in a batch gets submitted, and the steps in that job don't start queueing.

*Solution:* This appears to be related to the Globus access token timing out. You can fix this by logging out and logging back in again. Note that an active, logged-in session does NOT ensure your token is active. We've asked Globus to look into helping address this.

=======================
Processing & Metrics
=======================

*Problem:* I have many fewer reads in my data than I was expecting from the BaseSpace/Illumina run data.

*Solution:* If the libraries were separated between flow cell lanes, then a preprocessing script MUST be run to set up the FASTQ directories appropriately. See :ref:`rnaseqproc-getdata` for more details.

------------

*Problem:* The wrapup script indicates missing or empty data files.

*Solution:* There are a couple of factors that often contribute to this behavior. Check the following:

1. If the files in question are missing Picard metrics files this is caused by an issue with the .JAR on the Galaxy server and you need to re-process this library. You can do so by copying the batch submission file and deleting the lines for libraries with complete output.
2. If the files in question are missing counts, fastqs, or alignment files, there is an issue with the pipeline. Check to make sure that the job histories have completed without errors, that the BRI GridFTP endpoint is active, that the output directory has the correct permissions, and that the workflow batch file was generated with the correct output targets. 
3. If the files in question are Trinity, MiXCR, or alignment files that are empty, this is likely due to a low number of reads in the FASTQ. Check to ensure that the FASTQs have been pre-processed correctly (see above) and then check the file size of the merged input FASTQ file. If the file size is much lower than for comparable libraries, there is less sequence data and this behavior is expected.

-------------

*Problem:* The MiXCR step (or other jobs managed by SLURM) isn't producing output for some/all of the libraries.

*Solution:* There are two likely causes for this problem. Both can be diagnosed by refreshing 'squeue' and observing that jobs are rapidly submitted to and cleared from worker nodes. If all nodes are behaving equally, scenario (1) is more likely. If specific nodes appear to be clearing jobs too quickly, scenario (2) is more likely.

1. SLURM may not have write access to the directory where it writes its logging information. By default SLURM writes to a file called 'slurm.out' in the directory you call SLURM from. This behavior can be changed by passing arguments to the SLURM commands.
2. Some SLURM nodes may be unresponsive, even if the 'sinfo' command suggests that they're functional. In this case, contact BRI's helpdesk with the node names (ie: slurm[1-16]) and they can help reset and reconnect the nodes to the cluster pool.