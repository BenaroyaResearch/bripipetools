#!/bin/bash

################################################################################
# Process a 10X dataset using Cell Ranger
#
# Requirements:
# - cellranger installed at /opt/cellranger-4.0.0/cellranger
#
# Assumptions:
# - the script is being run from a server with the bfx and genomics directories
#   on Isilon mounted at /nfs/bioinformatics and /nfs/genomics
# - sample sheets are found in the gen core run directories, and are named
#   'SampleSheet.csv or Samplesheet.csv'
#
# Usage: 
# ./run_cellranger.sh []
#
# Mario Rosasco for BRI 2020
################################################################################

# default parameters
usage="Usage: $0 [args] [list of flow cell run IDs]\n
-----------------\n
# Optional Args\n
-----------------\n
-e <expectedNumberOfCells> (default: 5000)\n
-t <pathToTranscriptRef> (default: '/nfs/bioinformatics/pipeline/annotation/10x/GRCh38.91')\n
-v <pathToVdjRef> (default: '/nfs/bioinformatics/pipeline/annotation/10x/refdata-cellranger-vdj-GRCh38-alts-ensembl-4.0.0')\n
-r <flowCellIdPattern> (default: '[A-Za-z0-9]+(HV|M5)')\n
-o <summaryOutputDirectory> (default: '/nfs/bioinformatics/pipeline/tenxSummaries')\n
-c <cellRangerBinary> (default: '/opt/cellranger-4.0.0/cellranger')\n
-----------------\n
# Required Args\n
-----------------\n
-p <projectID> (eg: 'P377-1')\n
-d <processedDirName> (eg: '201023-CellRangerV4Manual_P377-1')\n
-w <workingDir> (eg: '/nfs/bioinformatics/workspace/mrosasco/201023-10XProcessingP377-1')\n
-s <cellRangerStep> (one of 'mkfastq', 'count', 'aggr', 'copyOutputs' or 'all')\n
<list of flow cell run IDs>\n
\n
Note that 'count' and 'all' will perform gene counting for GEX libraries, and 
VDJ identification for TCR libraries, based on the suffix of the sample name in
the sample sheet. GEX libraries should have a '_10X_GEX' suffix, and TCR
libraries should have a '_10X_TCR' suffix. The BAP 10X sample sheet generator 
will automatically append these suffixes.\n
\n
Also note that, as with the rest of the pipeline tools, there are very strong 
assumptions being made about file and directory structures. All of the stages 
in Cell Ranger can be run manually outside of this script for testing and 
exploration."

# default parameters
nCellsExpected=5000
fcIdRegex="[A-Za-z0-9]+(HV|M5)"
transcriptomeReference="/nfs/bioinformatics/pipeline/annotation/10x/GRCh38.91"
vdjReference="/nfs/bioinformatics/pipeline/annotation/10x/refdata-cellranger-vdj-GRCh38-alts-ensembl-4.0.0"
outputDir="/nfs/bioinformatics/pipeline/tenxSummaries"
cellRangerBin="/opt/cellranger-4.0.0/cellranger"

# user-set params
while getopts ":p:d:w:s:e:t:v:r:o:c:" opt; do
  case $opt in
    p) 
      pid=$OPTARG
      ;;
    d)
      processedDirName=$OPTARG
      ;;
    w)
      processingDir=$OPTARG
      ;;
    s)
      cellRangerStep=$OPTARG
      ;;
    e)
      nCellsExpected=$OPTARG
      ;;
    t)
      transcriptomeReference=$OPTARG
      ;;
    r)
      fcIdRegex=$OPTARG
      ;;
    o)
      outputDir=$OPTARG
      ;;
    v)
      vdjReference=$OPTARG
      ;;
    c)
      cellRangerBin=$OPTARG
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

if [ ! "$cellRangerStep" ]
then
  echo "You must specify a Cell Ranger stage to run (-s argument)."
  echo -e $usage
  exit 1
fi

#==============================================================================
# Processing Variables
#==============================================================================
sampleSheetDir="${processingDir}/sampleSheets"
# shouldn't need to change the following on srvtenx02
genCoreRoot="/nfs/genomics/Illumina"
bfxCoreRoot="/nfs/bioinformatics/pipeline/Illumina"

# check required args 
if [ ! "$pid" ] || [ ! "$processedDirName" ] || [ ! "$processingDir" ]
then
  echo "Required arguments missing."
  echo -e $usage
  exit 1
fi

# remaining args should be flow cell runs.
# All steps require at least one flow cell run. 
shift $(($OPTIND - 1))
flowCellList="$@"
if [ ! "$flowCellList" ]; then
  echo "No flow cell runs provided. Exiting."
  echo -e $usage
  exit 1
fi

# Check the name pattern on the flow cells to make sure 
# they contain IDs we understand
for currFc in $flowCellList
do
  if $(echo $currFc | grep -Eqv ${fcIdRegex}); then
    echo "Could not detect flow cell IDs in all runs."
    echo "List of runs: ${flowCellList}"
    echo "Expected flow cell ID pattern: ${fcIdRegex}"
    exit 1
  fi
done

#==============================================================================
# Cell Ranger Stages Helper Functions
#==============================================================================
# prepSampleSheets(): Required globals
# user-set:
#   -flowCellList 
#   -processingDir
# static:
#   -sampleSheetDir
#   -fcIdRegex
#   -genCoreRoot
prepSampleSheets() {
  mkdir -p ${sampleSheetDir}
  for currFc in $flowCellList
  do
    currFcId=$(echo $currFc | grep -Eo ${fcIdRegex})
    
    # sometimes the file is camelcase, sometimes it's just capitalized
    if [ -f "${genCoreRoot}/${currFc}/SampleSheet.csv" ]; then
      cp ${genCoreRoot}/${currFc}/SampleSheet.csv ${sampleSheetDir}/${currFcId}_sampleSheet.csv
    elif [ -f "${genCoreRoot}/${currFc}/Samplesheet.csv" ]; then
      cp ${genCoreRoot}/${currFc}/Samplesheet.csv ${sampleSheetDir}/${currFcId}_sampleSheet.csv
    else
      echo "ERROR: Could not find sample sheet for flow cell ${currFc}. Exiting."
      exit 1
    fi
  done
}
#==============================================================================
# runMkfastq(): Required globals
# user-set:
#   -flowCellList
#   -processedDirName
#   -pid
#   -processingDir (as part of sampleSheetDir)
# static:
#   -sampleSheetDir
#   -fcIdRegex
#   -genCoreRoot
#   -bfxCoreRoot
#   -cellRangerBin
runMkfastq() {
  for currFc in $flowCellList
  do
    # Make working dir
    workingDir="${bfxCoreRoot}/${currFc}/${processedDirName}"
    mkdir -p $workingDir
    cd $workingDir
    
    # get the fcid to use to distinguish pools/reruns/etc
    currFcId=$(echo $currFc | grep -Eo ${fcIdRegex})
    
    ${cellRangerBin} mkfastq \
    --id=${pid}_mkfastq_${currFcId} \
    --run=${genCoreRoot}/${currFc}/ \
    --samplesheet=${sampleSheetDir}/${currFcId}_sampleSheet.csv \
    --qc
  done
}
#==============================================================================
# runCount(): Required globals
# user-set:
#   -flowCellList
#   -processedDirName
#   -processingDir (as part of sampleSheetDir)
#   -pid
# static:
#   -sampleSheetDir
#   -fcIdRegex
#   -genCoreRoot
#   -bfxCoreRoot
#   -cellRangerBin
#   -vdjReference
#   -transcriptomeReference
runCount() {
  for currFc in $flowCellList
  do
    # set working dir and move there
    workingDir="${bfxCoreRoot}/${currFc}/${processedDirName}"
    cd $workingDir
    
    # get the fcid to use to distinguish pools/reruns/etc
    currFcId=$(echo $currFc | grep -Eo ${fcIdRegex})
    echo "Processing libraries in flow cell ${currFcId}..."
    
    # parse sample sheet to get libids
    currSampleSheet=${sampleSheetDir}/${currFcId}_sampleSheet.csv
    allLibs=$(cat $currSampleSheet | grep -Eo "^lib[0-9]+" | sort | uniq)
    
    # for each libid, generate counts or run vdj caller
    for currLib in $allLibs
    do
      echo "Processing library ${currLib}"
      currSample=$(cat $currSampleSheet | grep -E "^$currLib" | cut -d, -f2 | uniq)
      
      if $(echo ${currSample} | grep -q TCR); then
        echo "TCR library detected (sample name: ${currSample}). Running 'vdj'..."
        ${cellRangerBin} vdj \
        --id=$currLib \
        --fastqs=${pid}_mkfastq_${currFcId}/outs/fastq_path \
        --reference=${vdjReference} \
        --sample=$currSample
        
      elif $(echo ${currSample} | grep -q GEX); then
        echo "GEX library detected (sample name: ${currSample}). Running 'counts'..."
        ${cellRangerBin} count \
        --id=$currLib \
        --transcriptome=${transcriptomeReference} \
        --fastqs=${pid}_mkfastq_${currFcId}/outs/fastq_path \
        --sample=$currSample \
        --expect-cells=5000
        
      else
        echo "Error: Could not detect sample type (sample: ${currSample})"
        stop
      fi
    done
  done
}
#==============================================================================
# runAggr(): Required globals
# user-set:
#   -flowCellList
#   -processedDirName
#   -processingDir
#   -pid
# static:
#   -sampleSheetDir
#   -fcIdRegex
#   -genCoreRoot
#   -bfxCoreRoot
#   -cellRangerBin
#   -vdjReference
#   -transcriptomeReference
runAggr() {
  aggrManifest="${processingDir}/$(date +"%y%m%d")-aggrManifest.csv"
  
  # write .csv header
  printf "library_id,molecule_h5\n" > $aggrManifest
  
  # process each flow cell
  for currFc in $flowCellList
  do
    # set working dir 
    workingDir="${bfxCoreRoot}/${currFc}/${processedDirName}"
    
    # get the fcid to use to distinguish pools/reruns/etc
    currFcId=$(echo $currFc | grep -Eo $fcIdRegex)
    
    # parse sample sheet to get libids
    currSampleSheet="${workingDir}/${pid}_mkfastq_${currFcId}/outs/input_samplesheet.csv"
    allLibs=$(cat $currSampleSheet | grep -Eo "^lib[0-9]+" | sort | uniq)
    
    # for each libid, print line into aggr manifest
    for currLib in $allLibs
    do
      currSample=$(cat $currSampleSheet | grep -E "^$currLib" | cut -d, -f2 | uniq)
      if $(echo ${currSample} | grep -q GEX); then
        echo "Looking in ${workingDir} for lib ${currLib} from sample ${currSample}"
        
        currMolFile="${workingDir}/${currLib}/outs/molecule_info.h5"
        printf "%s,%s\n" $currLib $currMolFile >> $aggrManifest
      fi
    done
  done
  
  # move to project director for last flow cell in list, and run cellranger aggr
  cd "${bfxCoreRoot}/${currFc}/${processedDirName}"
  ${cellRangerBin} aggr \
  --id=${pid}_aggr \
  --normalize none \
  --csv=$aggrManifest
}
#==============================================================================
# copyOutputs(): Required globals
# user-set:
#   -flowCellList
#   -processedDirName
#   -processingDir
#   -pid
# static:
#   -sampleSheetDir
#   -fcIdRegex
#   -genCoreRoot
#   -bfxCoreRoot
#   -cellRangerBin
#   -vdjReference
#   -transcriptomeReference
copyOutputs() {
  # set up summary directory
  summaryDir="${outputDir}/$(date +"%y%m%d")-${pid}"
  mkdir -p $summaryDir
  
  # collect outputs and rename according to library ID
  for currFc in $flowCellList
  do
    # get the fcid to use to distinguish pools/reruns/etc
    currFcId=$(echo $currFc | grep -Eo ${fcIdRegex})
    
    # parse sample sheet to get libids
    currSampleSheet="${sampleSheetDir}/${currFcId}_sampleSheet.csv"
    allLibs=$(cat $currSampleSheet | grep -Eo "^lib[0-9]+" | sort | uniq)
    
    # copy data for each lib
    for currLibid in $allLibs
    do
      libDir="${bfxCoreRoot}/${currFc}/${processedDirName}/${currLibid}/outs"
      
      # copy files
      currSample=$(cat $currSampleSheet | grep -E "^$currLibid" | cut -d, -f2 | uniq)
      
      if $(echo ${currSample} | grep -q "TCR"); then
        mkdir -p ${summaryDir}/tcr
        cp ${libDir}/web_summary.html ${summaryDir}/tcr/${currLibid}_web_summary.html
        cp ${libDir}/vloupe.vloupe ${summaryDir}/tcr/${currLibid}_vloupe.vloupe
        cp ${libDir}/clonotypes.csv ${summaryDir}/tcr/${currLibid}_clonotypes.csv
        cp ${libDir}/all_contig_annotations.csv ${summaryDir}/tcr/${currLibid}_all_contig_annotations.csv
        cp ${libDir}/metrics_summary.csv ${summaryDir}/tcr/${currLibid}_metrics_summary.csv
      elif $(echo ${currSample} | grep -q "GEX"); then
        mkdir -p ${summaryDir}/gex/
        cp ${libDir}/web_summary.html ${summaryDir}/gex/${currLibid}_web_summary.html
        cp ${libDir}/cloupe.cloupe ${summaryDir}/gex/${currLibid}_cloupe.cloupe
        cp ${libDir}/molecule_info.h5 ${summaryDir}/gex/${currLibid}_molecule_info.h5
        cp ${libDir}/raw_feature_bc_matrix.h5 ${summaryDir}/gex/${currLibid}_raw_feature_bc_matrix.h5
        cp ${libDir}/metrics_summary.csv ${summaryDir}/gex/${currLibid}_metrics_summary.csv
      else
        echo "ERROR - UNEXPECTED SAMPLE NAME ${currSample}"
      fi
    done
  done
  
  # copy over aggregated files for GEX libs if the aggregation directory exists
  aggrDir="${bfxCoreRoot}/${currFc}/${processedDirName}/${pid}_aggr/outs"
  
  if [ -d "$aggrDir" ]; then
    mkdir -p ${summaryDir}/aggregated/
    cp ${aggrDir}/web_summary.html ${summaryDir}/aggregated/${pid}_aggr_noNorm_web_summary.html
    cp ${aggrDir}/cloupe.cloupe ${summaryDir}/aggregated/${pid}_aggr_noNorm_cloupe.cloupe
    cp ${aggrDir}/raw_feature_bc_matrix.h5 ${summaryDir}/aggregated/${pid}_aggr_noNorm_raw_feature_bc_matrix.h5
    cp ${aggrDir}/aggregation.csv ${summaryDir}/aggregated/${pid}_aggregation.csv
  fi
}


#==============================================================================
# Main program flow - 
# run different cellranger stages 
#==============================================================================
if [ $cellRangerStep = "mkfastq" ]; then
  
  echo "Running stage 'mkfastq'..."
  prepSampleSheets
  runMkfastq
  
elif [ $cellRangerStep = "count" ] || [ $cellRangerStep = "vdj" ]; then 

  echo "Running stages 'count' and/or 'vdj' for libraries..."
  runCount
  
elif [ $cellRangerStep = "aggr" ]; then 
  
  echo "Running stages 'aggr' for GEX libraries..."
  runAggr

elif [ $cellRangerStep = "copyOutputs" ]; then 

  echo "Copying outputs from the list of flow cell runs..."
  copyOutputs
  
elif [ $cellRangerStep = "all" ]; then 
  
  echo "Running all stages..."
  prepSampleSheets
  runMkfastq
  runCount
  runAggr
  copyOutputs
  
else 
  echo "No match found for requested process ${cellRangerStep}. Exiting."
  exit 1
fi
