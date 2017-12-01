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

    usedLanes=`echo $firstFolder | grep -Eo L[0-9]+`
    
    for currFolder in $libFolders
    do
      if [ "$currFolder" != "$firstFolder" ]
      then
        # figure out the lane ID for the current folder
        currLane=`echo $currFolder | grep -Eo L[0-9]+`
        newLane=$currLane
        if [[ $usedLanes == *$currLane* ]]
        then
          if [[ $usedLanes == *"L003"* ]]
          then
            newLane="L004"
          else
            newLane="L003"
          fi
        fi
        usedLanes=$usedLanes$newLane
        
        # For each folder after the first, copy the fastq file into the first
        fromPath=$dataFolder/$projFolder/$fastqFolder/$currFolder
        toPath=$dataFolder/$projFolder/$fastqFolder/$firstFolder
        
        sourceFiles=`ls $fromPath`
        echo "Found files" `ls $fromPath`
        #echo "Moving files from" $currFolder "to" $firstFolder
        #cp $fromPath/* $toPath
        for f in $sourceFiles
        do
          destf=`echo $f | sed s/$currLane/$newLane/g`
          echo "Changing file" $f "to" $destf
          #mv $fromPath/$f $toPath/$destf
        done
        
        # Remove the old folder 
        # renamedFolder=`echo $currFolder | sed s/lib/dup/g`
        echo "Deleting" $currFolder
        rm -rf $dataFolder/$projFolder/$fastqFolder/$currFolder
      fi
    done
  done
done