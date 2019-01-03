#!/bin/bash

################################################################################
# Fix paths to fastq files from new BaseSpace directory structure
#
# Sets up unaligned fastq directory structure for ease of use in bripipetools,
# and so that path names don't get too long to be usable
# 
# Usage: 
# ./fix_new_basespace_lanes.sh <flow cell run folder>
#
################################################################################
usage="Usage: $0 <flow cell run folder>"

if [ -z "$1" ]
then
    echo $usage
    exit
fi

runFolder=$1
dataFolder=$runFolder/Unaligned
projFolders=`ls $dataFolder | grep "P[0-9]*-[0-9]*"`
manifestPath=$runFolder/Unaligned/$(date +'%y%m%d')-fileManifest.tsv

# check if manifest already exists
if [ -e $runFolder/Unaligned/*fileManifest.tsv ]
then
  echo WARNING: Manifest file already located in $runFolder/Unaligned/
  echo Halting execution
  exit 1
fi

# write header to manifest
echo -e originalPath'\t'newPath >> $manifestPath

for projFolder in $projFolders
do
  # get the list of all the library ids in the project - note that there can be
  # multiple fastq folders that we need to handle
  fastqFolders=`ls $dataFolder/$projFolder`
  for fastqFolder in $fastqFolders
  do
    allLibs=`ls $dataFolder/$projFolder/$fastqFolder | cut -d '_' -f 1 | uniq`

    # Collect the folders for each lib
    for lib in $allLibs
    do
      echo "Handling library" $lib
      # make the target directory for the library
      toPath=$dataFolder/$projFolder/$lib
      [ -e $toPath ] || mkdir $toPath
      
      libFolders=`ls $dataFolder/$projFolder/$fastqFolder | grep $lib`
      for currFolder in $libFolders
      do
        # Move the fastq file into the target directory
        fromPath=$dataFolder/$projFolder/$fastqFolder/$currFolder
        echo "Found files" `ls $fromPath`
        echo "Moving files to" $projFolder/$lib
        
        for currDataFile in `ls $fromPath`
        do
          newDataFile=$currDataFile
          # first check and make sure data file of same name doesn't already exist
          # This can happen if, eg: there were 2 fastq generation procedures run 
          # on the same flow cell
          while [ -e $toPath/$newDataFile ]
          do
            tmpDataFile=${newDataFile}_2
            echo WARNING: File $toPath/$newDataFile exists. Renaming to $tmpDataFile
            newDataFile=$tmpDataFile
          done
          
          mv $fromPath/$currDataFile $toPath/$newDataFile
          echo -e $fromPath/$currDataFile'\t'$toPath/$newDataFile >> $manifestPath
          rmdir $fromPath
        done
      done
    done
    rmdir $dataFolder/$projFolder/$fastqFolder
  done
done