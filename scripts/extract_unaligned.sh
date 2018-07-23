#!/bin/bash

################################################################################
# Extract unaligned reads in a .bam file
#
# Requirements:
# - samtools
# - seqtk
#
# Assumptions:
# - the project folder contains a subfolder called "alignments"
# - the project folder contains another directory called "inputFastqs"
# - within the alignments folder are bam files with .bam extensions
# - the .bam files contain unmapped reads
# - within the inputFastqs folder are fastqs corresponding to the bamfiles
# - both the .bams and the .fastqs are named with an ID matching lib[0-9]+
#
# Usage: 
# ./extract_unaligned.sh [-d <project dir>] [-f <bam file>]
# setting either -d or -f is required. If -d is set, -f is ignored.
#
# Mario Rosasco for BRI 2018
################################################################################

# default parameters
usage="Usage: $0 [-d <project dir>] [-f <bam file>]"

# user-set params
while getopts ":d:f:" opt; do
  case $opt in
    d) 
      workingdir=$OPTARG
      ;;
    f)
      workingfile=$OPTARG
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

if [ ! "$workingdir" ] && [ ! "$workingfile" ]
then
  echo "You must specify a bam file or project directory."
  echo "Note that setting a project directory supercedes setting a bam file."
  echo $usage
  exit 1
fi

# get the alignments
if [ "$workingdir" ]
then
  all_alignments=$(ls $workingdir/alignments/ | grep bam$)
elif [ "$workingfile" ]
then
  all_alignments=$workingfile
  # set working dir to one folder above dir where alignment is
  workingdir=$(dirname $(dirname $workingfile))
fi

# make a directory for storing the unmaped reads
mkdir $workingdir/unmapped

# process alignments
for alignment in $(basename $all_alignments)
do
  # set up file names
  echo "Processing file $alignment..."
  unmappedsam=$(echo $alignment | sed 's/_alignments.bam/_unmapped.sam/')
  unmappedlst=$(echo $alignment | sed 's/_alignments.bam/_unmapped.lst/')
  unmappedfastq=$(echo $alignment | sed 's/_alignments.bam/_unmapped.fastq/')
  
  # get indices for unmapped reads and generate read names
  echo "Retrieving unmapped indices..."
  samtools view -f4 $workingdir/alignments/$alignment > \
    $workingdir/unmapped/$unmappedsam
  
  cut -f1 $workingdir/unmapped/$unmappedsam | sort | \
    uniq > $workingdir/unmapped/$unmappedlst
    
  # extract the fastq info corresponding to the unmapped reads
  echo "Extracting unmapped fastq information..."
  libid=$(echo $alignment | grep -Eo "lib[0-9]+")
  fastq=$(find $workingdir/inputFastqs -regex .*$libid.*)
  seqtk subseq $fastq $workingdir/unmapped/$unmappedlst > \
    $workingdir/unmapped/$unmappedfastq
  echo "Wrote unmapped fastq file to $workingdir/unmapped/$unmappedfastq"
done

