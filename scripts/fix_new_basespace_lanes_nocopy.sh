#!/bin/bash

runFolder=$1
dataFolder=$runFolder/Unaligned
projFolders=`ls $dataFolder | grep "P[0-9]*-[0-9]*"`

for projFolder in $projFolders
do
  # get the list of all the libraries in the project
  fastqFolder=`ls $dataFolder/$projFolder`
  allLibs=`ls $dataFolder/$projFolder/$fastqFolder | cut -d '_' -f 1 | uniq`

  # Collect the folders for each lib
  for lib in $allLibs
  do
    echo "Handling library" $lib
    libFolders=`ls $dataFolder/$projFolder/$fastqFolder | grep $lib`
    firstFolder=`echo $libFolders | cut -d ' ' -f 1`
    for currFolder in $libFolders
    do
      if [ "$currFolder" != "$firstFolder" ]
      then
        # For each folder after the first, copy the fastq file into the first
        fromPath=$dataFolder/$projFolder/$fastqFolder/$currFolder
        toPath=$dataFolder/$projFolder/$fastqFolder/$firstFolder
        echo "Found files" `ls $fromPath`
        echo "Moving files from" $currFolder "to" $firstFolder
        mv $fromPath/* $toPath
        
        # Change the name of the old folder to "dup****" rather than "lib****"
        renamedFolder=`echo $currFolder | sed s/lib/dup/g`
        echo "Renaming" $currFolder "to" $renamedFolder
        mv $dataFolder/$projFolder/$fastqFolder/$currFolder\
         $dataFolder/$projFolder/$fastqFolder/$renamedFolder
      fi
    done
  done
done

# make a folder to hold the (now duplicated) lib folders
dupFolder=$dataFolder/DupFromNewBasespace/
mkdir $dupFolder
find $dataFolder -name "*dup*" -exec mv {} $dupFolder \;