#!/bin/bash

################################################################################
# Generate Project and Library Reference Lists 
#
# searches for projects and libraries (based on file name regex)
# and writes lists of projects and libraries to files
#
# Usage: 
# ./generate_project_lib_lists.sh [-apl] [-d <root search dir>] [-n <search depth>]
# 
# -p|l|a: indicates type of list: [p]roject, [l]ibrary, or [a]ll (default)
#
# -d <root search dir> (default is current dir)
#
# -n <search depth> (default is 1)
#
# Assumptions:
# - All projects are related to an ".../Unaligned/{projectID}" folder under root
# - All libraries are related to a ".../fastq.gz" file under root
# 
# NB: searching with depth >4 can be very slow in the genomics directories!
################################################################################

# default parameters
workingdir=$(pwd)
searchdepth=1
find_projects=true
find_libs=true

# user-set params
while getopts ":plad:n:" opt; do
  case $opt in
    a)
      find_projects=true
      find_libs=true
      ;;
    p)
      find_libs=false
      find_projects=true
      ;;
    l)
      find_projects=false
      find_libs=true
      ;;
    d) 
      workingdir=$OPTARG
      ;;
    n)
      searchdepth=$OPTARG
      ;;
    \? )
      echo "Usage: $0 [-a|p|l] [-d <root search dir>] [-n <search depth>]"
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument."
      echo "Usage: $0 [-a|p|l] [-d <root search dir>] [-n <search depth>]"
      exit 1
      ;;
  esac
done

# set up file names for output
proj_file=project_list_$(date +'%y%m%d').txt
lib_file=lib_list_$(date +'%y%m%d').txt

# get list of all projects
if [ "$find_projects" = true ]
then
  echo "Now traversing directory to find projects..."
  cd $workingdir
  echo "ProjectFastqDirectory" > $proj_file
  find "`pwd`" -maxdepth $searchdepth -regex ".*/Unaligned/[Project_]*P[0-9]+[a-zA-Z0-9-]*" |\
   sort >> $proj_file
fi

# get list of libraries
if [ "$find_libs" = true ]
then
  echo "Now traversing directory to find libraries..."
  cd $workingdir
  libpaths=$(find "`pwd`" -maxdepth $searchdepth -regex ".*\.fastq.gz$" | grep -E lib[0-9]+)
  
  printf "libID\tlibFolder\tflowcellFolder\tprojectFolder\tserverLocation\tfilePath\n" > $lib_file
  for libpath in $libpaths
  do
    ### grep -Eo will return all matches; use awk instead
    libid=$(echo "$libpath" | \
      awk 'match($0, /lib[0-9]+/){ print substr($0, RSTART, RLENGTH) }')
    libfolder=$(echo "$libpath" | \
      awk 'match($0, /\/[^\/]*lib[0-9]+[^\/]*\//){ print substr($0, RSTART, RLENGTH) }')
    fcfolder=$(echo "$libpath" | \
      awk 'match($0, /\/[^\/]*[a-zA-Z0-9]+X[X|Y|2][^\/]*\//){ print substr($0, RSTART, RLENGTH) }')
    projfolder=$(echo "$libpath" |\
      awk 'match($0, /\/[^\/]*P[0-9]+[^\/]*\//){ print substr($0, RSTART, RLENGTH) }')
    projid=$(echo "$libpath" |\
      awk 'match($0, /P[0-9]+[a-zA-Z0-9-]*/){ print substr($0, RSTART, RLENGTH) }')
    serverloc=$(echo "$libpath" |\
      awk 'match($0, '$fcfolder'){ print substr($0, 0, RSTART-1) }')
    filepath=$(echo "$libpath" | xargs dirname)
    
    printf "%s\t%s\t%s\t%s\t%s\t%s\n" $libid $libfolder $fcfolder $projfolder $serverloc $filepath
  done >> $lib_file
  
  # clean up duplicates and globus-generated FASTQs. This is an ugly fix...
  awk '!seen[$0]++' $lib_file > tmp.txt
  mv tmp.txt $lib_file
  cat $lib_file | awk '!/inputFastqs/' > tmp.txt
  mv tmp.txt $lib_file
fi
