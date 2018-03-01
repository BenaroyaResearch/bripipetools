#!/bin/bash

# Inputs:
# GTF file for the genome annotation release
# BAM file (only header is used)
# Output:
# Generates a picard-style interval list file with the same name as the GTF 
# and the extension ".ribosomalIntervalsWheader.txt"


GTF_IN=$1
BAM_IN=$2

GTF_DIR=$(basename $GTF_IN)

# strip extension
GTF_BASE=${GTF_IN%.*}

RIBO_INTS_OUT="${GTF_BASE}.ribosomalIntervalsWheader.txt"

echo "Saving RibosomalIntervals file as ${RIBO_INTS_OUT}..."

samtools view -H $BAM_IN > $RIBO_INTS_OUT

grep rRNA $GTF_IN > ribo.tmp.txt
paste <(cut -f 1 ribo.tmp.txt) <(cut -f 4-5 ribo.tmp.txt) <(cut -f 7 ribo.tmp.txt) <(cut -f 9 ribo.tmp.txt) >> $RIBO_INTS_OUT

rm ribo.tmp.txt
