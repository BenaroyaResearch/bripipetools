#!/bin/bash

################################################################################
# Generate SNP Variant Call Files for a Library
#
# Runs mpileup and bcftools call to call variants from a bamfile.
#
# Requirements:
#   - samtools
#   - bcftools
# 
# Usage: 
# ./call_lib_snps.sh <bamfile> <output dir> <bedfile>
#
################################################################################
usage="Usage: $0 <bamfile> <output dir> <bedfile>"

if [ -z "$3" ]
then
    echo $usage
    exit
fi

infile=$1
outdir=$2
bedfile=$3

refAssemblyFile="/mnt/genomics/mrosasco/annotation/GRCh38/Homo_sapiens.GRCh38.dna.primary_assembly.fa"

echo "Processing $infile"

bcf_outfile=$outdir/$(echo $infile | grep -oE lib[0-9]+_[A-Z0-9]+)_samtools-mpileup_snps.bcf
vcf_outfile=$outdir/$(echo $infile | grep -oE lib[0-9]+_[A-Z0-9]+)_bcftools-call_snps.vcf
echo "Generating $bcf_outfile"
samtools mpileup -f $refAssemblyFile -B -C 50 -d 250 -l $bedfile -q 30 -Q 13 -g -e 20 -h 100 -L 250 -o 40 $infile -o $bcf_outfile

echo "Generating $vcf_outfile"
bcftools call -O v -c -o $vcf_outfile $bcf_outfile