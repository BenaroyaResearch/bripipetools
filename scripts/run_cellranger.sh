#!/bin/bash

################################################################################
# Run the stages of the Cell Ranger pipeline on a flow cell of 10X data
#
# Requirements:
# - Cell Ranger 
# - bcl2fastq
# - an isilon mount for the genomics shared directory
# - an isilon mount for the bioinformatics shared directory
#
# Note that this script should usually be run on srvtenx02, 
# which meets these requirements.
#
# Assumptions:
# - The bioinformatics and genomics directories both have a subdirectory for 
# the flow cell run(s), and the run directories share the same name
# - The sample sheet for the run is located in the genomics run directory and is
# named SampleSheet.csv 
#
# Mario Rosasco for BRI 2020
################################################################################

# default parameters
usage="Usage: $0  [options] <flow cell run list> \n
Available Options:\n
[-h] display help text then exit\n
[-p <projectID>] default: P000-0\n
[-n <procesingName>] default: CellRangerV4NoAdapterManual\n
[-d <datePrefix>] default: current date in YYMMDD format\n
[-v <cellRangerVersion>] default: 4.0.0\n
[-a <aggrNormMethod>] default: none\n
[-t <vdjReference>] default: .../refdata-cellranger-vdj-GRCh38-alts-ensembl-4.0.0\n
[-g <gexReference>] default: .../GRCh38.91\n
[-b <baseBfxDir>] default: /nfs/bioinformatics/pipeline/Illumina/\n
[-q <baseGenomicsDir>] default: /nfs/genomics/Illumina/
"

# naming/ID vars
currDate=$(date +"%y%m%d")
projectId="P000-0"
procName="CellRangerV4NoAdapterManual"

# cell ranger parameters
aggrNorm="none"
cellRangerVersion="4.0.0"

# locations
baseBfxDir="/nfs/bioinformatics/pipeline/Illumina"
baseGenDir="/nfs/genomics/Illumina/"
vdjRef="/nfs/bioinformatics/pipeline/annotation/10x/refdata-cellranger-vdj-GRCh38-alts-ensembl-4.0.0"
gexRef="/nfs/bioinformatics/pipeline/annotation/10x/GRCh38.91"

# user-set params
OPTIND=1 # reset getopts index in case of previous usage in curr session
while getopts ":hd:p:n:v:a:t:g:b:q:" opt; do
  case $opt in
    h)
      echo "
      This program will run the full Cell Ranger pipeline for a list of 
      BRI Genomics Core flow cell runs. This includes 'mkfastq' and either 
      'count' or 'vdj' depending on the library type. The library type is 
      determined based on the values in the 'Description' column of the sample 
      sheet, which should have values of '10X_GEX' or '10X_TCR' as appropriate. 
      As a final step, 'aggr' will be run on all gene expresion libraries, 
      with the output added to the processing directory of the last flow cell
      run listed.
      
      NB - This program assumes that the sample sheet in the genomics run
      directory is appropriate to use for Cell Ranger processing, and is named
      'SampleSheet.csv'. 
      "
      echo -e $usage
      exit 0
      ;;
    d) 
      currDate=$OPTARG
      ;;
    p)
      projectId=$OPTARG
      ;;
    n)
      procName=$OPTARG
      ;;
    v)
      cellRangerVersion=$OPTARG
      ;;
    a)
      aggrNorm=$OPTARG
      ;;
    t)
      vdjRef=$OPTARG
      ;;
    g)
      gexRef=$OPTARG
      ;;
    b)
      baseBfxDir=$OPTARG
      ;;
    q)
      baseGenDir=$OPTARG
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

# Argument Checking - Run IDs
shift $((OPTIND-1))
runList="$@"
if [ -z "$runList" ]; then
    echo "No runs were detected. You must supply at least 1 run (eg: 200811_VH00126_26_AAACCGWM5)."
    echo -e $usage
    exit 1
fi

# Argument checking - Version
case $cellRangerVersion in
  4.0.0) ;;
  3.1.0) ;;
  *)
    echo "The requested version ('$cellRangerVersion') is not supported."
    exit 1
    ;;
esac

echo "Beginning processing."
echo "Run List: $runList"
echo "Cell Ranger Version: $cellRangerVersion"

# process each flow cell
for currRun in $runList
do
  # Make working dir
  workingDir="${baseBfxDir}/${currRun}/${currDate}-${procName}_${projectId}"
  mkdir $workingDir
  cd $workingDir

  # get the fcid 
  currFcId=$(echo $currRun | grep -Eo "[A-Za-z0-9]+(M5|XX|XF|X2|X3)$")
  
  # get the sample sheet and get all lib info
  currSampleSheet=${baseGenDir}/${currRun}/SampleSheet.csv
  allLibs=$(cat $currSampleSheet | grep -Eo "^lib[0-9]+" | sort | uniq)
  
  #==============================================================================
  # MKFASTQ
  #==============================================================================
  echo "Generating library fastqs from flow cell ${currFcId}..."
  time /opt/cellranger-${cellRangerVersion}/cellranger mkfastq \
  --id=${projectId}_mkfastq_${currFcId} \
  --run=/nfs/genomics/Illumina/${currRun}/ \
  --samplesheet=${currSampleSheet}\
  --qc
  
  #==============================================================================
  # COUNT AND VDJ
  #==============================================================================
  # for each libid, generate counts or run vdj caller
  for currLib in $allLibs
  do
  echo "Processing library ${currLib}"
  currSample=$(cat $currSampleSheet | grep -E "^$currLib" | cut -d, -f2 | uniq)
  currDesc=$(cat $currSampleSheet | grep -E "^$currLib" | cut -d, -f8 | uniq)

  if $(echo ${currDesc} | grep -q TCR); then
   echo "TCR library detected (sample name: ${currSample}). Running 'vdj'..."
   /opt/cellranger-${cellRangerVersion}/cellranger vdj \
   --id=${currLib} \
   --fastqs=${projectId}_mkfastq_${currFcId}/outs/fastq_path \
   --reference=${vdjRef} \
   --sample=${currSample}
   
  elif $(echo ${currDesc} | grep -q GEX); then
    echo "GEX library detected (sample name: ${currSample}). Running 'counts'..."
   /opt/cellranger-${cellRangerVersion}/cellranger count \
   --id=${currLib} \
   --transcriptome=${gexRef} \
   --fastqs=${projectId}_mkfastq_${currFcId}/outs/fastq_path \
   --sample=${currSample} \
   --expect-cells=5000
   
  else
   echo "Error: Could not detect sample type (sample: ${currSample})"
   stop
  fi

  done
done

#==============================================================================
# AGGR
#==============================================================================
# build csv manifest for aggr
# note that we're still in the last run dir from above
aggrId="${projectId}_norm-${aggrNorm}_aggr"
aggrManifest="$(pwd)/${aggrId}_manifest.csv"

# write .csv header
printf "library_id,molecule_h5\n" > $aggrManifest

# process each flow cell
for currRun in $runList
do
  # set working dir and move there
  
  workingDir="${baseBfxDir}/${currRun}/${currDate}-${procName}_${projectId}"

  # get the fcid
  currFcId=$(echo $currRun | grep -Eo "[A-Za-z0-9]+(M5|XX|XF|X2|X3)$")

  # parse sample sheet to get libids
  currSampleSheet=${baseGenDir}/${currRun}/SampleSheet.csv
  allLibs=$(cat $currSampleSheet | grep -Eo "^lib[0-9]+" | sort | uniq)

  # for each libid, print line into aggr manifest
  for currLib in $allLibs
  do
    currSample=$(cat $currSampleSheet | grep -E "^$currLib" | cut -d, -f2 | uniq)
    currDesc=$(cat $currSampleSheet | grep -E "^$currLib" | cut -d, -f8 | uniq)
    if $(echo ${currDesc} | grep -q GEX); then
     echo "Looking in ${workingDir} for lib ${currLib} from sample ${currSample}"

     currMolFile="${workingDir}/${currLib}/outs/molecule_info.h5"
     printf "%s,%s\n" $currLib $currMolFile >> $aggrManifest
    fi

  done
done

# run cellranger aggr
/opt/cellranger-${cellRangerVersion}/cellranger aggr \
--id=${aggrId} \
--csv=$aggrManifest \
--normalize ${aggrNorm}

