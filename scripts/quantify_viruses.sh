#!/bin/bash

################################################################################
# Quantify viral sequence counts from unmapped reads
#
# Requirements:
# - samtools
# - bowtie and an appropriate index
# - a copy of "submit_align_count.sh" in the same directory as this script
#
# Assumptions:
# - The project folder contain a folder called "unmapped" that contains files of
#   the form <libid>_<flowcellid>_sam-to-fastq_unmapped.fastq
#
# Usage: 
# ./quantify_viruses.sh [-q <query>] [-f <flowcell dir>] [-p <project dir>] 
#                       [-i <bowtie index name>]
#
# Mario Rosasco for BRI 2018
################################################################################

# default parameters
usage="Usage: $0 [-q <query>] [-f <flowcell>] [-p <project dir>] [-i <bowtie index name>]"
idx="/mnt/genomics/mrosasco/viral/rvdb-human-lowvec-nohiv"

# user-set params
while getopts ":i:q:f:p:" opt; do
  case $opt in
    i) 
      idx=$OPTARG
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

# function to run blastn on a query
# usage: run_blast_for_query <query> <idx>
quant_viruses_for_query()
{
  squery=$1
  sidx=$2
  
  workingdir=$(dirname $squery)
  workingfile=$(basename $squery)
  idxname=$(basename $sidx)
  
  outdir=$(dirname $workingdir)/count_unmapped_$idxname
  outfile_align=${workingfile%%.*}_${idxname}_bowtie.sam
  outfile_cts=${workingfile%%.*}_${idxname}_counts.tsv
  
  mkdir $outdir
  echo "Aligning $workingfile to idx $idxname"
  
  sbatch -N 1 --exclusive -J $workingfile -o $outdir/${workingfile}_align_count.out $(dirname $0)/submit_align_count.sh $sidx $squery $outdir/$outfile_align $outdir/$outfile_cts
}

# run the alignment(s) for the appropriate queries
if [ "$flowcell" ]; then
  echo "Processing flowcell $flowcell..."
  projects=$(find $flowcell -maxdepth 2 -name unmapped -exec dirname {} \;)
  for currp in $projects
  do
    echo "Processing project $currp..."
    queries=$(find $currp/unmapped -name "*sam-to-fastq_unmapped.fastq")
    for currq in $queries
    do
      quant_viruses_for_query $currq $idx
    done
  done
  exit 0
  
elif [ "$project" ]; then
  echo "Processing project $project..."
  queries=$(find $project/unmapped -name "*sam-to-fastq_unmapped.fastq")
  for currq in $queries
  do
    quant_viruses_for_query $currq $idx
  done
  
elif [ "$query" ]; then
  quant_viruses_for_query $query $idx
  exit 0
  
else
  echo "You must specify a query file, a project folder, or a flowcell folder."
  echo "Note that setting a flowcell folder supercedes setting a project folder"
  echo "which in turn supercedes setting a query file."
  echo $usage
  exit 1 
fi

