#!/bin/bash

################################################################################
# Extract reads with a given fragment size range from paired-end alignments
#
# Requirements:
# - samtools
#
# Usage: 
# ./extractReadsBySize.sh
# -b <input bamfile>
# -a <minimum fragment length>
# -z <maximum fragment length>
# [-o <output bamfile>]
# [-s]
# [-h]
#
# Mario Rosasco for BRI 2020
################################################################################

# default parameters
usage="This script extracts all aligned reads in a bamfile with fragment sizes 
in a specified range. The extracted reads are written to a new BAM file.\n\n
Usage:
\n$0 \n
-b <input bamfile> (required)\n
[-a <minimum fragment length>] (optional - default 0)\n
[-z <maximum fragment length>] (optional - default 100)\n
[-o <output bamfile>] (optional - default FilteredReads.bam)\n
[-s] (optional - output in SAM format)\n
[-h] (print this message then exit)"
minFragmentSize=0
maxFragmentSize=100
outfile="FilteredReads.bam"

# user-set params
while getopts ":b:a:z:o:s" opt; do
  case $opt in
    b) 
      bamfile=$OPTARG
      ;;
    a)
      minFragmentSize=$OPTARG
      ;;
    z)
      maxFragmentSize=$OPTARG
      ;;
    o)
      outfile=$OPTARG
      ;;
    s)
      keepSam=1
    ;;
    h)
      echo -e $usage
      exit 0
    ;;
    \? )
      echo -e $usage
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument."
      echo -e $usage
      exit 1
      ;;
  esac
done

# check for appropriate input
if [ ! "$bamfile" ]; then 
  echo "You must specify a bamfile with the argument '-b <bamfile>'. Please try again."
  echo -e $usage
  exit 1
elif [ ! -f $bamfile ]; then
  echo "Could not find a bamfile named '$bamfile'. Please try again."
  echo -e $usage
  exit 1
elif [ $minFragmentSize -gt $maxFragmentSize ]; then 
  echo "The minimum fragment size must be less than or equal to the maximum fragment size."
  exit 1
fi

echo "Copying header into new SAM file..."
samtools view -H $bamfile > $outfile

echo "Filtering file ${bamfile} to select reads with a fragment size range of [${minFragmentSize}, ${maxFragmentSize}]..."
#samtools view $bamfile | awk -v minFrag="$minFragmentSize" -v maxFrag="$maxFragmentSize" 'function abs(v) {return v < 0 ? -v : v} {if (abs($9) > minFrag && abs($9) < maxFrag) print;}' >> $outfile
samtools view $bamfile | \
awk -v minFrag="$minFragmentSize" -v maxFrag="$maxFragmentSize" 'function abs(v) {return v < 0 ? -v : v} {if (abs($9) >= minFrag && abs($9) <= maxFrag) print;}' \
>> $outfile

if [ "$keepSam" ] && [ "$keepSam" -eq "1" ]; then
  echo "Keeping SAM format."
  echo "Processing completed. Filtered SAM file saved as ${outfile} Exiting."
  exit 0
else
  echo "Converting to BAM format..."
  mv $outfile tmpSamForConversion.sam
  samtools view -b tmpSamForConversion.sam > $outfile
  rm tmpSamForConversion.sam
  echo "Processing completed. Filtered BAM file saved as ${outfile} Exiting."
  exit 0
fi
