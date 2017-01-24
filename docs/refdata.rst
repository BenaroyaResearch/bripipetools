.. _refdata-page:

**************
Reference Data
**************

.. _refdata-prep:

Preparing annotation data
=========================

Genome FASTA
------------

(describe)

Gene model GTF
--------------

(describe)

Gene model RefFlat
------------------

(describe)

Ribosomal intervals
-------------------

(describe)

SNP Panel
---------

VCF file (``all_grch37.vcf``) obtained here:

https://github.com/gatoravi/maury


Based on this study:

https://www.ncbi.nlm.nih.gov/pubmed/24070238


Saved at:

``/mnt/genomics/reference_data/annotationsForGalaxy/GRCh38/all_grch37.vcf``

(even though it's not GRCh38)


Re-mapped to GRCh38 using NCBI remap tool:

https://www.ncbi.nlm.nih.gov/genome/tools/remap/

GRCh37 (hg19) -> GRCh38 (hg38)


Converted to BED using ``bedops``:

::

    vcf2bed --snvs < all_grch38.vcf > all_grch38.bed


Uploaded to Globus Galaxy. Added to data library.


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

-----

.. _refdata-upload:

Uploading to Galaxy library
===========================

(steps)
