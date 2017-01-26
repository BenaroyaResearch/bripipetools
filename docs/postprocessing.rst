.. _postprocess-page:

********************
Post-processing Data
********************

Postprocessing nominally entails any operations performed on data `after` it has left Galaxy (or more generally, outside the scope of a bioinformatics processing workflow).

.. _postprocess-validate:

QC & validation
===============

QC here is geared less on intrinsic qualities of the data, but on leveraging what is known about the samples (i.e., through the BRI GenLIMS or Sample Repository databases) to identify potential sample swaps or other problematic mixups.

Sex check validation
--------------------

The ``bripipetools.qc.sexcheck`` modules inspect X and Y chromosome gene counts for each processed library, provide a predicted sex value, compare this prediction to any reported sex value that exists in the database, and reports the status.

SNP fingerprinting
------------------

**[PENDING]** These modules would compare SNP profiles from either 1) a panel of common, highly discriminative SNPs, 2) all mitochondrial SNPs, or possibly 3) all common SNPs to confirm that libraries generated from the same subject match as expected.

-----


.. _postprocess-org:

File naming & organization
==========================

``postprocessing`` package
--------------------------

Modules in the ``postprocessing`` package are used to parse, combine, rename, and organize files as needed such that they fit the desired layout.

Current (Globus)
^^^^^^^^^^^^^^^^

No more crazy nesting or zipping. More explicitly labeled files. This organization also includes combined outputs across all samples for ``QC`` and ``validation`` data; furthermore, combined ``QC``, ``metrics``, and ``validation`` data are merged into a single table at the project level labeled ``combined_summary_data``.

This particular organization (including the addition of parsed and combined QC and validation data) entered production with the ``161014_D00565_0133_AC9E23ANXX`` flowcell (the handful prior were similar in terms of nesting and labeling, but did not include the full assortment of files).

Note: the ``bripipetools.postprocessing.cleanup`` is designed to convert organization and naming from older schemes into the current structure, prior to other postprocessing steps (stitching, compiling). Such cleanup may be unnecessary if output files are parsed and imported directly into GenLIMS.

::

    Project_P123-10Processed_globus_161017/
    ├── P123-10_C9E23ANXX_161017_combined_summary_data.csv
    ├── QC
    │   ├── P123-10_C9E23ANXX_161017_combined_overrep_seqs.csv
    │   ├── P123-10_C9E23ANXX_161017_combined_qc.csv
    │   ├── lib13364_C9E23ANXX_fastqc_qc.html
    │   └── lib13364_C9E23ANXX_fastqc_qc.txt
    ├── Trinity
    │   ├── Trinity_combined1.fa
    │   ├── Trinity_combined2.fa
    │   └── lib13364_C9E23ANXX_trinity.fasta
    ├── alignments
    │   ├── lib13364_C9E23ANXX_tophat_alignments.bam
    │   └── lib13364_C9E23ANXX_tophat_alignments.bam.bai
    ├── counts
    │   ├── P123-10_C9E23ANXX_161017_combined_counts.csv
    │   └── lib13364_C9E23ANXX_htseq_counts.txt
    ├── log
    │   └── lib13364_C9E23ANXX_workflow_log.txt
    ├── metrics
    │   ├── P123-10_C9E23ANXX_161017_combined_metrics.csv
    │   ├── P123-10_geneModelCoverage.pdf
    │   ├── lib13364_C9E23ANXX_htseq_metrics.txt
    │   ├── lib13364_C9E23ANXX_picard_align_metrics.html
    │   ├── lib13364_C9E23ANXX_picard_markdups_metrics.html
    │   ├── lib13364_C9E23ANXX_picard_rnaseq_metrics.html
    │   └── lib13364_C9E23ANXX_tophat_stats_metrics.txt
    ├── mixcrOutput_trinity
    │   ├── lib13364_mixcrAlign.vdjca
    │   ├── lib13364_mixcrAlignPretty.txt
    │   ├── lib13364_mixcrAssemble.clns
    │   ├── lib13364_mixcrClns.txt
    │   └── lib13364_mixcrReport.txt
    ├── trimmed
    │   └── lib13364_C9E23ANXX_trimmed.fastq
    └── validation
        ├── P123-10_C9E23ANXX_161017_combined_validation.csv
        └── lib13364_C9E23ANXX_sexcheck_validation.csv



Old (Globus)
^^^^^^^^^^^^

Similar to the local organization, the initial Globus organization included various degrees of nesting, zipping, and crytpic naming (this was with the intention of matching the old structure). A few notes:

* ``inputFastqs``: these files represent concatenated lane-specific FASTQ files for a library; there's no real reason for these to be output from workflows or saved long term (this behavior will change in future versions)
* ``metrics``: the zipped archives in this folder behave a bit different than with the local org, as contents are extracted directly to the ``metrics`` folder, rather than as a new uncompressed folder; I might have fixed this at some point, but it's something to watch out for
* ``TrimmedFastqs``: these represent FASTQs after adapter and quality trimming; they also don't need ot be saved

This organization was used through the ``160817_D00565_0129_BC97JMANXX`` flowcell.

::

    Project_P135-1Processed_globus_160622/
    ├── QC
    │   └── lib12112_C8LB7ANXX
    │       ├── qcR1
    │       │   ├── fastqc_data.txt
    │       │   └── fastqc_report.html
    │       └── qcR1.zip
    ├── TrimmedFastqs
    │   └── lib12112_C8LB7ANXX_trimmed.fastq
    ├── Trinity
    │   ├── Trinity_combined1.fa
    │   ├── Trinity_combined2.fa
    │   └── lib12112_C8LB7ANXX
    │       └── Trinity.fasta
    ├── alignments
    │   ├── lib12112_C8LB7ANXX.bam
    │   └── lib12112_C8LB7ANXX_tophat_alignments.bam.bai
    ├── counts
    │   ├── P135-1_C8LB7ANXX_160622_combined_counts.csv
    │   └── lib12112_C8LB7ANXX_count.txt
    ├── inputFastqs
    │   └── lib12112_C8LB7ANXX_R1-final.fastq.gz
    ├── logs
    │   └── lib12112_C8LB7ANXX_workflow_log.txt
    ├── metrics
    │   ├── P135-1_C8LB7ANXX_160622_combined_metrics.csv
    │   ├── P135-1_geneModelCoverage.pdf
    │   ├── lib12112_C8LB7ANXXMarkDups.zip
    │   │   └── (MarkDups_Dupes_Marked_html.html)
    │   ├── lib12112_C8LB7ANXX_al.zip
    │   │   └── (RNA_Seq_Metrics_html.html)
    │   ├── lib12112_C8LB7ANXX_qc.zip
    │   │   └── (Picard_Alignment_Summary_Metrics_html.html)
    │   ├── lib12112_C8LB7ANXXmm.txt
    │   └── lib12112_C8LB7ANXXths.txt
    └── mixcrOutput_trinity
        ├── lib12112_mixcrAlign.vdjca
        ├── lib12112_mixcrAlignPretty.txt
        ├── lib12112_mixcrAssemble.clns
        ├── lib12112_mixcrClns.txt
        └── lib12112_mixcrReport.txt


Old (local)
^^^^^^^^^^^

The old file organization (used when workflows were run on a local Galaxy server and cluster) includes a lot of nesting, zipping, and cryptic naming.

For instance, metrics file abbreviations can be decoded as follows:

* ``_qc``: Picard Alignment Summary Metrics
* ``_al``: Picard CollectRnaSeqMetrics
* ``MarkDups``: Picard MarkDuplicates
* ``ths``: Tophat Stats
* ``mm``: htseq-count "other counts"

The last flowcell for which this organization was used exclusively is ``160307_D00565_0103_BC893JANXX`` (note: projects were processed both locally and with Globus Genomics for the next handful of flowcells until ``160609_D00565_0113_BC8LB7ANXX``, in which operations transferred completely to Globus)

::

    Project_P43-41Processed_160311/
    ├── P43-41_C893JANXX_160311_pulldownLog.txt
    ├── QC
    │   └── lib10852_C893JANXX
    │       ├── qcR1
    │       │   ├── FastQC_FastqMcf_on_data_69_and_data_68__reads_html.html
    │       │   ├── FastqMcf_on_data_69_and_data_68__reads_fastqc.zip
    │       │   ├── duplication_levels.png
    │       │   ├── error.png
    │       │   ├── fastqc_data.txt
    │       │   ├── fastqc_icon.png
    │       │   ├── fastqc_report.html
    │       │   ├── kmer_profiles.png
    │       │   ├── per_base_gc_content.png
    │       │   ├── per_base_n_content.png
    │       │   ├── per_base_quality.png
    │       │   ├── per_base_sequence_content.png
    │       │   ├── per_sequence_gc_content.png
    │       │   ├── per_sequence_quality.png
    │       │   ├── rgFastQC96yA9X.log
    │       │   ├── sequence_length_distribution.png
    │       │   ├── summary.txt
    │       │   ├── tick.png
    │       │   └── warning.png
    │       └── qcR1.zip
    ├── TrimmedFastqs
    │   └── lib10852_C893JANXX_trimmed.fastq
    ├── Trinity
    │   ├── Trinity_combined1.fa
    │   └── lib10852_C893JANXX
    │       └── Trinity.fasta
    ├── alignments
    │   ├── lib10852_C893JANXX.bam
    │   └── lib10852_C893JANXX.bam.bai
    ├── alignments_noDups
    │   ├── lib10852_C893JANXX_noDups.bam
    │   └── lib10852_C893JANXX_noDups.bam.bai
    ├── counts
    │   ├── P43-41_C893JANXX_160311_combined_counts.csv
    │   └── lib10852_C893JANXX_count.txt
    ├── metrics
    │   ├── P43-41_C893JANXX_160311_combined_metrics.csv
    │   ├── P43-41_geneModelCoverage.pdf
    │   ├── lib10852_C893JANXXMarkDups
    │   │   ├── MarkDuplicates.log
    │   │   ├── MarkDuplicates.metrics.txt
    │   │   └── MarkDups_Dupes_Marked_html.html
    │   ├── lib10852_C893JANXXMarkDups.zip
    │   ├── lib10852_C893JANXX_al
    │   │   ├── CollectRnaSeqMetrics.log
    │   │   ├── CollectRnaSeqMetrics.metrics.txt
    │   │   └── RNA_Seq_Metrics_html.html
    │   ├── lib10852_C893JANXX_al.zip
    │   ├── lib10852_C893JANXX_qc
    │   │   ├── CollectAlignmentSummaryMetrics.log
    │   │   ├── CollectAlignmentSummaryMetrics.metrics.txt
    │   │   └── Picard_Alignment_Summary_Metrics_html.html
    │   ├── lib10852_C893JANXX_qc.zip
    │   ├── lib10852_C893JANXXmm.txt
    │   └── lib10852_C893JANXXths.txt
    └── mixcrOutput_trinity
        ├── lib10852_mixcrAlign.vdjca
        ├── lib10852_mixcrAlignPretty.txt
        ├── lib10852_mixcrAssemble.clns
        ├── lib10852_mixcrClns.txt
        └── lib10852_mixcrReport.txt

