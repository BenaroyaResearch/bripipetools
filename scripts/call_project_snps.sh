#!/bin/bash

################################################################################
# Generate SNP Variant Call Files for a Project
#
# Looks in a target project directory for bam files and then calls SNPs for
# each lib in the alignment folder using the `call_lib_snps.sh` script.
# Creates a slurm job for each library, so must be run on the cluster.
# 
# Usage: 
# ./call_project_snps.sh <flowcell directory>
#
################################################################################
usage="Usage: $0 <project directory>"

if [ $# -eq 0 ]
then
    echo $usage
    exit
fi

projectdir=$1
mkdir $projectdir/snps

for infile in $(ls $projectdir/alignments/ | grep -E .bam$)
do
  echo "Processing $infile"
  sbatch -N 1 --exclusive -J $infile -o $projectdir/snps/${infile}_slurm.out ./call_lib_snps.sh $projectdir/alignments/$infile $projectdir/snps
done

