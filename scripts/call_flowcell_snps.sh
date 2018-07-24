#!/bin/bash

################################################################################
# Generate SNP Variant Call Files for a Flow Cell
#
# Looks in a target flow cell directory for project folders and then calls SNPs 
# for each lib in the project folder using the `call_project_snps.sh` script.
# Creates a slurm job for each library, so must be run on the cluster.
# 
# Usage: 
# ./call_flowcell_snps.sh <flow cell directory>"
#
################################################################################
usage="Usage: $0 <flow cell directory>"

if [ $# -eq 0 ]
then
    echo $usage
    exit
fi

fcdir=$1

projects=`ls $fcdir | grep -E "Project_P[0-9]+"`

for p in $projects
do
  echo "Calling SNPs for project "$p
  ./call_project_snps.sh <flowcell directory>
done
