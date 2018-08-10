#!/bin/bash

################################################################################
# Generate SNP Variant Call Files for a Library
#
# Looks in a target project directory for bam files and then calls SNPs for
# each lib in the alignment folder using the `call_lib_snps.sh` script.
# 
# Usage: 
# ./call_lib_snps.sh <bamfile> <output dir>
#
################################################################################
usage="Usage: $0 <bamfile> <output dir>"

if [ -z "$2" ]
then
    echo $usage
    exit
fi

infile=$1
outdir=$2

echo "Processing $infile"

bcf_outfile=$outdir/$(echo $infile | grep -oE lib[0-9]+_[A-Z0-9]+)_samtools-mpileup_snps.bcf
vcf_outfile=$outdir/$(echo $infile | grep -oE lib[0-9]+_[A-Z0-9]+)_bcftools-call_snps.vcf
echo "Generating $bcf_outfile"
/mnt/genomics/bin/samtools mpileup -f /mnt/genomics/mrosasco/annotation/GRCh38/Homo_sapiens.GRCh38.dna.primary_assembly.fa -B -C 50 -d 250 -l /mnt/genomics/mrosasco/annotation/snp_ref/GRCh38_NGSCheckMate_andInterestingSNP.bed -q 30 -Q 13 -g -e 20 -h 100 -L 250 -o 40 $infile -o $bcf_outfile

echo "Generating $vcf_outfile"
bcftools call -O v -c -o $vcf_outfile $bcf_outfile