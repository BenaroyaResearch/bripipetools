#!/bin/bash

#reflat part is from https://gist.github.com/igordot/4467f1b02234ff864e61, this if or gtf format 2 used by Ensembl

GTF_IN=$1
GTF_DIR=$(basename $GTF_IN)

# strip extension
GTF_BASE=${GTF_IN%.*}

REFFLAT_OUT="${GTF_BASE}.refflat.txt"

echo "Saving RefFlat file as ${REFFLAT_OUT}..."

gtfToGenePred -genePredExt -geneNameAsName2 $GTF_IN refFlat.tmp.txt
paste <(cut -f 12 refFlat.tmp.txt) <(cut -f 1-10 refFlat.tmp.txt) > $REFFLAT_OUT
rm refFlat.tmp.txt

