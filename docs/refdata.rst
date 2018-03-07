.. _refdata-page:

**************
Reference Data
**************

.. _refdata-prep:

Preparing annotation data
=========================

Genome FASTA
------------

Either download through `Ensembl <http://uswest.ensembl.org/info/data/ftp/index.html>`_, `iGenomes <http://support.illumina.com/sequencing/sequencing_software/igenome.html>`_, or ask Globus Genomics support to build index for you.

Gene model GTF
--------------

Either download through `Ensembl <http://uswest.ensembl.org/info/data/ftp/index.html>`_, `iGenomes <http://support.illumina.com/sequencing/sequencing_software/igenome.html>`_, or ask Globus Genomics support to build index for you.

Gene model RefFlat
------------------

Either download through `iGenomes <http://support.illumina.com/sequencing/sequencing_software/igenome.html>`_ or build using ``gtf_to_refflat.sh``.

Ribosomal intervals
-------------------

Either build using ``generate_ribo_ints_ref.sh`` or in Globus Galaxy using **Generate_Ribosomal_Reference_File** workflow.

SNP Panel for Sample Identification
-----------------------------------

NGSCheckMate SNP panel (``GRCh38_NGSCheckMateSNP``) obtained `here <https://github.com/parklab/NGSCheckMate/blob/master/SNP/SNP_GRCh37_hg19_wChr.bed>`_, based on `this study <https://www.ncbi.nlm.nih.gov/pubmed/28369524>`_

Re-mapped to GRCh38 using UCSC `LiftOver tool <https://genome.ucsc.edu/cgi-bin/hgLiftOver>`_:

GRCh37 (hg19) -> GRCh38 (hg38)

Uploaded to Globus Galaxy and added to data library as GRCh38_NGSCheckMateSNP.bed.


Non-mitochondrial BED file
--------------------------

::

    samtools view -H lib6839_C6VG0ANXX.bam \
        | cut -f 2,3 \
        | awk '{gsub(/(SN:|LN:)/, ""); print}' \
        | egrep -v "^(K|G|M|I|V)" \
        | awk '{printf ("%s\t1\t%s\n", $1, $2)}' \
        > grch38_mitofilter.bed


::

    samtools view -H mm9.bam | cut -f 2,3 | awk '{gsub(/(SN:|LN:)/, ""); print}' | egrep -v "^(chrM|chrUn|I|V)" | grep -v "_random" |  awk '{printf ("%s\t1\t%s\n", $1, $2)}' > mm9_mitofilter.bed


Library prep (and other) adapters
---------------------------------

The main adapter reference file used for workflows is ``smarter_adapter_seqs_3p_5p.fasta``, which includes adapter sequences for the Nextera library prep kits.

-----


.. _refdata-upload:

Uploading to Galaxy library
===========================

1. Create a new history or use existing **ref_file_upload** history.
2. Upload file to current history directly (``Get Data`` -> ``Upload File``) or using Globus transfer (``Globus Data Transfer`` -> ``Get Data via Globus``).
3. Go to the **Shared Data** -> **Data Libraries** page.
4. Navigate to the annotation library and the relevant subfolder for the new annotation file.
5. Click on the file icon with a plus sign that says "Add Datasets to Current Folder" and chose "from History".
6. Select the history in which the annotation file dataset was added.
7. Select the file and click "Add".