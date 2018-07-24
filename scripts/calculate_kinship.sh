#!/bin/bash

################################################################################
# Calculate Kinship Values From SNP Variant Call Files 
#
# Looks in a target directory for projects with SNP calls and .lst files,
# then performs a kinship coefficient estimate (Manichaikul et al. 2012)
# for the libraries in each .lst file. By comparing the intra-subject kinship
# values (which should be high) to the inter-subject kinship values, 
# (which should be low), potential sample swaps can be identified and corrected.
# 
# Note that in the absence of the `-a` option, it is assumed that the 'snps'
# directory for each project contains one .vcf file per library, which will be
# used to generate the "all-libs.lst" family file for kinship analysis.
# 
# Usage: 
# ./calculate_kinship.sh -d <flowcell directory> [-s] [-m]
# 
# -d <flowcell directory>: the location of a project containing a snps folder
#
# -m turns OFF MDS value calculation by KING
# -a turns OFF auto-generation of an all-libs_family.lst file
#
################################################################################
usage="Usage: $0 -d <flowcell directory> [-m] [-a]"

kingflags="--kinship --duplicate --mds"
buildfamfile=true
# get user-set params
while getopts ":d:sm" opt; do
  case $opt in
    d)
      workingdir=$OPTARG
      ;;
    m)
      kingflags="--kinship --duplicate"
      ;;
    a)
      buildfamfile=false
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

if [ -z "$workingdir" ]
then
  echo $usage
  exit 1
fi

# GET LISTS OF FAMILIES FROM TARGET FLOWCELL FOLDER 
cd $workingdir
snpdirs=$(find "`pwd`" -name snps)
for dir in $snpdirs
do
  cd $dir
  
  # default mode: build an "all-libs.lst" family file
  if [ "$buildfamfile" = true ]
  then
    ls | grep -E ".vcf$" | sed 's/.vcf$//' > all-libs.lst
  fi

  
  # each .lst file should indicate a subject, containing a list of libraries 
  # that are labeled as originating from that subject
  # Because of the terminology of King, we'll call a subject a "family"
  allFam=`ls *.lst`
  for f in $allFam
  do
    echo "Processing $f..."
    
    libraries=()
    # family (subject) name
    export b=`basename $f .lst`
    export p=$b"-patient"
    export pvcf=$b"-patient.vcf"
    export pbed=$b"-patient.bed"

    for l in `cat $f`
    do
        libname=$l".vcf"
        gzname=$l".vcf.gz"
        echo "Checking for $gzname..."
        # Create the gzipped file if it doesn't exist
        if [ ! -f $gzname ]; then
          echo "$gzname not found. Creating from $libname..."
          bgzip -f $libname
          
          echo "Indexing $gzname"
          tabix -f -p vcf $gzname
        fi
        
        # reheader to Family_libname to prevent duplicate names
        export temp=`mktemp -t tempXXXXXX`

        export lib=`echo $gzname | egrep -o 'lib[0-9]+'`
        echo $b"_"$lib > $temp
        bcftools reheader -s $temp $gzname  > m.$gzname
        mv m.$gzname $gzname
        tabix -f -p vcf $gzname
        rm -f $temp
        
        
        libraries+=($gzname)
    done

    echo ${libraries[@]}
    bcftools merge ${libraries[@]} -o $pvcf
    plink2 --allow-extra-chr --vcf $pvcf --make-bed --out $p
    king -b $pbed --prefix $p $kingflags
    
  done
  
done
