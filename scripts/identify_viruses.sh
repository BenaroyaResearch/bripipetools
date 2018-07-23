#!/bin/bash

################################################################################
# Identify viral sequences from a list of assembeld contigs
#
# Requirements:
# - blast
# - slurm
# - a copy of "submit_blastn.sh" in the same directory as this script
#
# Assumptions:
# - The project folder contain a folder called "unmapped"
#
# Usage: 
# ./identify_viruses.sh [-q <query>] [-f <flowcell dir>] [-p <project dir>] 
#                       [-d <database name>]
#
# Mario Rosasco for BRI 2018
################################################################################

# default parameters
usage="Usage: $0 [-q <query>] [-f <flowcell>] [-p <project dir>] [-d <database name>]"
db="/mnt/genomics/mrosasco/viral/rvdb"

# user-set params
while getopts ":d:q:f:p:" opt; do
  case $opt in
    d) 
      db=$OPTARG
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
# usage: run_blast_for_query <query> <db>
run_blast_for_query()
{
  squery=$1
  sdb=$2
  
  workingdir=$(dirname $squery)
  workingfile=$(basename $squery)
  dbname=$(basename $sdb)
  
  outdir=$(dirname $workingdir)/blast_unmapped_$dbname
  outfile=${workingfile%%.*}_$dbname.csv
  
  mkdir $outdir
  #cmd="blastn -db $db -query $squery -out $outdir/$outfile -outfmt 10"
  echo "Aligning $workingfile to db $dbname"
  #TODO: SLURM THIS
  sbatch -N 1 --exclusive -J $workingfile -o $outdir/${workingfile}_blast.out ./submit_blastn.sh $sdb $squery $outdir/$outfile
  #$cmd
}

# run the alignment(s) for the appropriate queries
if [ "$flowcell" ]; then
  echo "Processing flowcell $flowcell..."
  projects=$(find $flowcell -maxdepth 2 -name unmapped -exec dirname {} \;)
  for currp in $projects
  do
    echo "Processing project $currp..."
    queries=$(find $currp/unmapped -name *.fasta)
    for currq in $queries
    do
      run_blast_for_query $currq $db
    done
  done
  exit 0
  
elif [ "$project" ]; then
  echo "Processing project $project..."
  queries=$(find $project/unmapped -name *.fasta)
  for currq in $queries
  do
    run_blast_for_query $currq $db
  done
  
elif [ "$query" ]; then
  run_blast_for_query $query $db
  exit 0
  
else
  echo "You must specify a query file, a project folder, or a flowcell folder."
  echo "Note that setting a flowcell folder supercedes setting a project folder"
  echo "which in turn supercedes setting a query file."
  echo $usage
  exit 1 
fi

