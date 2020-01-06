.. _methods-page:

**********************
Common methods summary
**********************

The following paragraphs describe the methods used in different workflows managed by *bripipetools*. These paragraphs are meant to serve as boilerplate for methods sections in manuscripts. Note that there are sometimes subtle differences different workflows, so be sure to choose the workflow description that's appropriate for your project.

.. warning:: **Versions of Local Tools**

   Note that the tool versions on Galaxy should be stable for a given workflow. However, on occasion BRI will upgrade tool versions that we use on our analysis and processing servers. In particular, the version of MiXCR used in the pipeline has changed with time. The following descriptions reference the most recent version of MiXCR used, but the :ref:`databases-tcr` collection in :ref:`resdb-intro` contains information on the exact version used to process each library. 

---------

Current Workflows
=================

Human, Bulk, Nextera Libraries, STAR Aligner
--------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). FastqMcf (v1.1.2) was used to remove any remaining adapter sequence. To align the trimmed reads, we used the STAR aligner (v2.4.2a) with the GRCh38 reference genome and gene annotations from ensembl release 91. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

Human, Single Cell, Nextera Libraries, STAR Aligner, Trinity Assembler
----------------------------------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). FastqMcf (v1.1.2) was used to remove any remaining adapter sequence. To align the trimmed reads, we used the STAR aligner (v2.4.2a) with the GRCh38 reference genome and gene annotations from ensembl release 91. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1). To identify TCR chains, the Trinity assembler was used to generate contigs. TCR sequences were identified and annotated from these contigs using MiXCR (v2.1.3).

Mouse, Bulk, Nextera Libraries, STAR Aligner
--------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). FastqMcf (v1.1.2) was used to remove any remaining adapter sequence. To align the trimmed reads, we used the STAR aligner (v2.4.2a) with the GRCm38 reference genome and gene annotations from ensembl release 91. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

Human, Bulk, TruSeq Libraries, STAR Aligner
-------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). To align the trimmed reads, we used the STAR aligner (v2.4.2a) with the GRCh38 reference genome and gene annotations from ensembl release 91. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

Human, Bulk, TruSeq Libraries, STAR Aligner, Trinity Assembler
--------------------------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). To align the trimmed reads, we used the STAR aligner (v2.4.2a) with the GRCh38 reference genome and gene annotations from ensembl release 91. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1). To identify TCR chains, the Trinity assembler was used to generate contigs. TCR sequences were identified and annotated from these contigs using MiXCR (v2.1.3).

Mouse, Bulk, TruSeq Libraries, STAR Aligner
-------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). To align the trimmed reads, we used the STAR aligner (v2.4.2a) with the GRCm38 reference genome and gene annotations from ensembl release 91. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

-----------

Legacy Workflows
=================

Human, Bulk, Nextera Libraries, TopHat Aligner
----------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). FastqMcf (v1.1.2) was used to remove any remaining adapter sequence. To align the trimmed reads, we used the TopHat aligner (v1.4.1) with the GRCh38 reference genome and gene annotations from ensembl release 77. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

Human, Single Cell, Nextera Libraries, TopHat Aligner, Trinity Assembler
------------------------------------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). FastqMcf (v1.1.2) was used to remove any remaining adapter sequence. To align the trimmed reads, we used the TopHat aligner (v1.4.1) with the GRCh38 reference genome and gene annotations from ensembl release 77. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1). To identify TCR chains, the Trinity assembler was used to generate contigs. TCR sequences were identified and annotated from these contigs using MiXCR (v2.1.3).

Mouse, Bulk, Nextera Libraries, TopHat Aligner
----------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). FastqMcf (v1.1.2) was used to remove any remaining adapter sequence. To align the trimmed reads, we used the TopHat aligner (v1.4.1) with the NCBIM37 reference genome and gene annotations from ensembl release 68. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

Human, Bulk, TruSeq Libraries, TopHat Aligner
---------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). To align the trimmed reads, we used the TopHat aligner (v1.4.1) with the GRCh38 reference genome and gene annotations from ensembl release 77. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

Human, Bulk, TruSeq Libraries, TopHat Aligner, Trinity Assembler
----------------------------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). To align the trimmed reads, we used the TopHat aligner (v1.4.1) with the GRCh38 reference genome and gene annotations from ensembl release 77. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1). To identify TCR chains, the Trinity assembler was used to generate contigs. TCR sequences were identified and annotated from these contigs using MiXCR (v2.1.3).

Mouse, Bulk, TruSeq Libraries, TopHat Aligner
---------------------------------------------
Reads were processed using workflows managed on the Galaxy platform. Reads were trimmed by 1 base at the 3’ end, and then trimmed from both ends until base calls had a minimum quality score of at least 30 (Galaxy FASTQ Trimmer tool v1.0.0). To align the trimmed reads, we used the TopHat aligner (v1.4.1) with the NCBIM37 reference genome and gene annotations from ensembl release 68. Gene counts were generated using HTSeq-count (v0.4.1). Quality metrics were compiled from PICARD (v1.134), FASTQC (v0.11.3), Samtools (v1.2), and HTSeq-count (v0.4.1).

-----------