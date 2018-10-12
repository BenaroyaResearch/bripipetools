#!/bin/bash

################################################################################
# Call SNPs from an alignment file, project, or flow cell
#
# Requirements:
# - blast
# - slurm
# - a copy of "call_lib_snps.sh" in the same directory as this script
#
# Assumptions:
# - The project folder contain a folder called "alignments"
#
# Usage: 
# ./call_snps.sh [-q <query>] [-f <flowcell dir>] [-p <project dir>] 
#                       [-b <bedfile name>] [-o <output dir name>]
#
# Mario Rosasco for BRI 2018
################################################################################

# default parameters
usage="Usage: $0 [-q <query>] [-f <flowcell>] [-p <project dir>] [-b <bedfile name>] [-o <output dir name>]"
bedfile="/mnt/genomics/mrosasco/annotation/snp_ref/GRCh38_NGSCheckMate_andInterestingSNP.bed"
outdirname="snps"

# user-set params
while getopts ":b:q:f:p:o:" opt; do
  case $opt in
    b) 
      bedfile=$OPTARG
      ;;
    q)
      query=$OPTARG
      ;;
    p)
      project=$OPTARG
      ;;
    f)
      flowcell=$OPTARG
      ;;
    o)
      outdirname=$OPTARG
      ;;
    \? )
      echo $usage
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument."
      echo $usage
      exit 1
      ;;
  esac
done

# function to call snps using mpileup and samtools call on a query
# usage: call_snps_for_query
call_snps_for_query()
{
  squery=$1
  sbed=$2
  soutname=$3
  
  workingdir=$(dirname $squery)
  workingfile=$(basename $squery)
  
  outdir=$(dirname $workingdir)/$soutname
  
  mkdir $outdir
  
  echo "Submitting $infile to slurm..."
  sbatch -N 1 --exclusive -J $workingfile -o $outdir/${workingfile}_slurm.out ./call_lib_snps.sh $squery $outdir $sbed
}

# run the alignment(s) for the appropriate queries
if [ "$flowcell" ]; then
  echo "Calling snps for projects in flowcell $flowcell..."
  projects=$(find $flowcell -maxdepth 2 -name alignments -exec dirname {} \;)
  for currp in $projects
  do
    echo "Processing project $currp..."
    queries=$(find $currp/alignments -name "*.bam")
    for currq in $queries
    do
      call_snps_for_query $currq $bedfile $outdirname
    done
  done
  exit 0
  
elif [ "$project" ]; then
  echo "Processing project $project..."
  queries=$(find $project/alignments -name "*.bam")
  for currq in $queries
  do
    call_snps_for_query $currq $bedfile $outdirname
  done
  
elif [ "$query" ]; then
  call_snps_for_query $query $bedfile $outdirname
  exit 0
  
else
  echo "You must specify a query (bam) file, a project folder, or a flowcell folder."
  echo "Note that setting a flowcell folder supercedes setting a project folder"
  echo "which in turn supercedes setting a query file."
  echo $usage
  exit 1 
fi

