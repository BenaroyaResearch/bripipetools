"""
Tools to handle databasing 10X datasets
"""

import os
import re
import csv
import json
import datetime
import click

import logging
import bripipetools
from bripipetools.database.operations import insert_objects, put_genomicsMetrics, put_genomicsSamples

from pymongo.errors import BulkWriteError

# connect to database
logger = logging.getLogger()
logger.info("Starting `bripipetools' tenx utilities`")
RDB = bripipetools.database.connect("researchdb")

#========================================
# database insert decorators
#========================================
@insert_objects('genomicsTenxVdj')
def put_genomicsTenxVdj(db, vdjData):
    """
    Insert each document in list into 'genomicsTenxVdj' collection.
    """
    return db, vdjData
    
@insert_objects('genomicsFiles')
def put_genomicsFiles(db, fileInfo):
    """
    Insert each document in list into 'genomicsFiles' collection.
    """
    return db, fileInfo

#========================================
# data preparation functions
#========================================
# procDirPath: A string representing a path of the form:
# /mount/path/to/data/flow_cell_run/10x_processing_dir/
def processTenxResults(procDirPath):
    # clean run path and extract run ID, flow cell ID
    procDirPath = os.path.normpath(procDirPath)
    procDir = os.path.basename(procDirPath)
    runPath = os.path.dirname(procDirPath)
    runId = os.path.basename(runPath)
    dataRoot = os.path.dirname(runPath)
    fcId = runId.split("_")[-1] # assume FC ID is last, always has been
    
    # get directory contents
    contents = [os.path.join(procDirPath, p) for p in os.listdir(procDirPath)]
    fqMatches = [match for match in contents if re.search("mkfastq", match)]
    libMatches = [match for match in contents if re.search("lib[0-9]+", match)]
    fqDirs = [fqDir for fqDir in fqMatches if os.path.isdir(fqDir)]
    libDirs = [libDir for libDir in libMatches if os.path.isdir(libDir)]
    
    # check expectations about directory structure
    if(len(fqDirs) > 1 or len(fqDirs) == 0):
        exit("ERROR: Expected exactly one 'mkfastq' directory, found " + str(len(fqDirs)))
    sampleSheetPath = os.path.join(fqDirs[0], "outs", "input_samplesheet.csv")
    if(not os.path.exists(sampleSheetPath)):
        exit("ERROR: Expected sample sheet at " + sampleSheetPath)
        
    # sniff project ID from mkfastq dir
    pids = re.findall("P[0-9]+-[0-9]+", os.path.basename(fqDirs[0]))
    if(len(pids) != 1):
        exit("ERROR: Could not sniff project ID (P#-#). Found " + str(len(pids)) + " matches.")
    pid = pids[0]
        
    # check sample names and annotations to try and determine GEX/VDJ libs 
    vdjLibs = []
    gexLibs = []
    with open(sampleSheetPath, newline='') as sampleSheet:
        sampleReader = csv.reader(sampleSheet)
        for row in sampleReader:
            # check library info and 
            if(re.match("lib[0-9]+", row[0])):
                rowStr = "_".join(row).lower()
                isTcrLib = ("vdj" in rowStr or "tcr" in rowStr)
                isGexLib = ("gex" in rowStr)
                libDirExists = os.path.exists(os.path.join(procDirPath, row[0]))
                
                if(isTcrLib and isGexLib):
                    exit("ERROR: Library " + row[0] + " appears to have both GEX and VDJ annotations.")
                elif(isTcrLib and libDirExists):
                    vdjLibs.append(row[0])
                elif(isGexLib and libDirExists):
                    gexLibs.append(row[0])
                elif (not libDirExists):
                    exit("ERROR: Library " + row[0] + " does not appear to have been processed.")
                else:
                    exit("ERROR: Could not determine type of library " + row[0])
        
        # process features common to VDJ and GEX - metrics and data file locs
        for currLib in gexLibs + vdjLibs:
            processTenxSamples(
                libId = currLib,
                fcId = fcId,
                runId = runId,
                projectId = pid
            )
            
            processTenxMetrics(
                procDirPath = procDirPath, 
                libId = currLib, 
                fcId = fcId
            )
            
            processLibraryFiles(
                procDirPath = procDirPath, 
                libId = currLib,
                fcId = fcId, 
                libOutPath = os.path.join(runId, procDir, currLib, "outs"), 
                dataRoot = dataRoot
            )
        
        # process data unique to VDJ libraries
        for currLib in vdjLibs:
            processVdjResults(
                procDirPath = procDirPath, 
                projectId = pid,
                libId = currLib, 
                runId = runId
            )

# refPath: A string representing a reference (genome, VDJ, etc)
# returns: 'mmu' or 'hsa' indicating m.musculus or h.sapiens repsectively
def getSpeciesFromRef(refPath):
    speciesDict = {
        'GRCm38.91': 'mmu',
        'GRCh38.91': 'hsa',
        'refdata-cellranger-vdj-GRCm38-alts-ensembl-4.0.0': 'mmu',
        'refdata-cellranger-vdj-GRCh38-alts-ensembl-4.0.0': 'hsa',
        'refdata-cellranger-vdj-GRCh38-alts-ensembl-3.1.0': 'hsa'
    }
    
    refName = os.path.basename(refPath)
    return speciesDict[refName]
    

# libPath: A string representing a path to the 10X processing dir 
# of the form: dataRoot/runId/procDir/currLib
# returns: dict with metadata (species, version #) mapped
def parseMetadata(libPath):
    versionFile = os.path.join(libPath, "_versions")
    invocationFile = os.path.join(libPath, "_invocation")
    if (not os.path.exists(versionFile)):
        exit("ERROR: file expected at " + versionFile + " could not be found.")
    if (not os.path.exists(invocationFile)):
        exit("ERROR: file expected at " + invocationFile + " could not be found.")
    
    # version already in json format, use as template
    with open(versionFile, 'r') as openFile:
        versionData=openFile.read()
    metadataDict = json.loads(versionData)
    
    # parse invocation file to get reference, use ref to parse species
    openFile = open(invocationFile, 'r')
    lines = openFile.readlines()
    for currLine in lines:
        currLine = re.sub(r"\"|,", "", currLine)
        currParts = currLine.strip().replace('"', '').split('=')
        if (currParts[0].strip() in ['reference_path', 'vdj_reference_path']):
            metadataDict.update({'referencePath' : currParts[1]})
            metadataDict.update({'species': getSpeciesFromRef(currParts[1])})
    
    return metadataDict
    
    
        
# procDirPath: A string representing a path of the form:
# /mount/path/to/data/flow_cell_run/10x_processing_dir
# projectId: A string of the form 'P###-##'
# libId: A string representing a BRI GenLIMS library ID
# runId: A string representing a flow cell run ID
def processVdjResults(procDirPath, projectId, libId, runId):
    # process contig data
    vdjPath = os.path.join(procDirPath, libId, "outs")
    dataFile = os.path.join(vdjPath, "all_contig_annotations.json")
    if(not os.path.exists(dataFile)):
        exit("ERROR: file expected at " + dataFile + " could not be found.")
    
    # collect metadata to add to collection
    metadata = parseMetadata(libPath = os.path.join(procDirPath, libId))
    
    with open(dataFile, 'r') as myfile:
        data=myfile.read()

    chainData = json.loads(data)
    # add an _id field comprising the libid and barcode id for each chain
    for i in range(0, len(chainData)):
        currChain = chainData[i]
        currChain.update({
            "metadata" : metadata,
            "libraryBarcodeId" : libId + "_" + currChain["barcode"],
            "libid": libId,
            "project": projectId,
            "run": runId,
            "dateCreated":  datetime.datetime.now(),
            "lastUpdated": datetime.datetime.now()
        })
        #put_genomicsTenxVdj(RDB, currChain)
        
    # check to see if libid is already in database
    libChainCheck = RDB['genomicsTenxVdj'].find_one({"libid": libId})
    if(libChainCheck is None):
        logger.info("Pushing chain data for {} VDJ contigs from library {}"
                    .format(len(chainData), libId))
        try:
            RDB['genomicsTenxVdj'].insert_many(chainData)
        except BulkWriteError as exc:
            print(exc.details)
    else: 
        logger.warning("Data for library {} already exists in the database. Skipping."
            .format(libId))

# procDirPath: A string representing a path of the form:
# /mount/path/to/data/flow_cell_run/10x_processing_dir
# libId: A string representing a BRI GenLIMS library ID
# fcId: A string representing a flow cell ID
def processTenxMetrics(procDirPath, libId, fcId):
    metricsPath = os.path.join(procDirPath, libId, "outs", "metrics_summary.csv")
    if(not os.path.exists(metricsPath)):
        exit("ERROR: file expected at " + metricsPath + " could not be found.")
    
    metricsData = []
    with open(metricsPath, newline='') as metricsFile:
        metricsReader = csv.reader(metricsFile)
        for row in metricsReader:
            metricsData.append(row)
    
    if(len(metricsData) != 2):
        exit(
            "ERROR: Expected metrics file to have 2 rows of data. " +
            "Found " + len(metricsData) + " rows in file " + metricsPath
        )
        
    # Names are human-readable, but pretty messy. 
    # Convert into something more programmer-friendly.
    metricsNamesDict = {
        "Estimated Number of Cells" : "estNumCells",
        "Mean Reads per Cell" : "meanReadsPerCell",
        "Median Genes per Cell" : "medianGenesPerCell",
        "Number of Reads" : "numReads",
        "Valid Barcodes" : "pctValidBarcodes",
        "Sequencing Saturation" : "pctSequencingSaturation",
        "Q30 Bases in Barcode" : "pctQ30BasesInBarcode",
        "Q30 Bases in RNA Read" : "pctQ30BasesInRNARead",
        "Q30 Bases in UMI" : "pctQ30BasesInUMI",
        "Reads Mapped to Genome" : "pctReadsMappedToGenome",
        "Reads Mapped Confidently to Genome" : "pctMappedConfidentlyToGenome",
        "Reads Mapped Confidently to Intergenic Regions" : "pctMappedConfidentlyToIntergenic",
        "Reads Mapped Confidently to Intronic Regions" : "pctMappedConfidentlyToIntronic",
        "Reads Mapped Confidently to Exonic Regions" : "pctMappedConfidentlyToExonic",
        "Reads Mapped Confidently to Transcriptome" : "pctMappedConfidentlyToTranscriptome",
        "Reads Mapped Antisense to Gene" : "pctMappedAntisenseToGene",
        "Fraction Reads in Cells" : "pctReadsInCells",
        "Total Genes Detected" : "totalGenesDetected",
        "Median UMI Counts per Cell" : "medianUmiCountsPerCell",
        "Mean Read Pairs per Cell" : "meanReadPairsPerCell",
        "Number of Cells With Productive V-J Spanning Pair" : "numCellsProductiveVJSpanning",
        "Number of Read Pairs" : "numReadPairs",
        "Q30 Bases in RNA Read 1" : "pctQ30BasesInRNARead",
        "Reads Mapped to Any V(D)J Gene" : "pctReadsMappedToAnyVdjGene",
        "Reads Mapped to TRA" : "pctReadsMappedToTra",
        "Reads Mapped to TRB" : "pctReadsMappedToTrb",
        "Mean Used Read Pairs per Cell" : "meanUsedReadPairsPerCell",
        "Median TRA UMIs per Cell" : "medianTraUmisPerCell",
        "Median TRB UMIs per Cell" : "medianTrbUmisPerCell",
        "Cells With Productive V-J Spanning Pair" : "pctCellsProductiveVJSpanning",
        "Cells With Productive V-J Spanning (TRA, TRB) Pair" : "pctCellsProductiveVJSpanningAlphaBetaPair",
        "Paired Clonotype Diversity" : "pairedClonotypeDiversity",
        "Cells With TRA Contig" : "pctCellsWithTraContig",
        "Cells With TRB Contig" : "pctCellsWithTrbContig",
        "Cells With CDR3-annotated TRA Contig" : "pctCellsWithCdr3AnnotatedTraContig",
        "Cells With CDR3-annotated TRB Contig" : "pctCellsWithCdr3AnnotatedTrbContig",
        "Cells With V-J Spanning TRA Contig" : "pctCellsWithVJSpanningTraContig",
        "Cells With V-J Spanning TRB Contig" : "pctCellsWithVJSpanningTrbContig",
        "Cells With Productive TRA Contig" : "pctCellsWithProductiveTraContig",
        "Cells With Productive TRB Contig" : "pctCellsWithProductiveTrbContig"
    }
    
    # rename keys
    metricsNames = []
    for currKey in metricsData[0]:
        metricsNames.append(metricsNamesDict[currKey])
        
    # clean numeric values
    metricsValues = []
    for currVal in metricsData[1]:
        cleanVal = re.sub("[^0-9\.]", "", currVal)
        metricsValues.append(float(cleanVal))
    
    # convert to dict
    metricsData = dict(zip(metricsNames, metricsValues))
    
    # collect metadata 
    metadata = parseMetadata(libPath = os.path.join(procDirPath, libId))
    
    # format like other metrics and add in metadata
    formattedMetrics = {
        "_id" : libId + "_" + fcId,
        "cellRanger" : metricsData,
        "metadata" : metadata,
        "dateCreated" :  datetime.datetime.now(),
        "lastUpdated" : datetime.datetime.now(),
        "libraryId" : libId,
        "flowcellId" : fcId,
        "type" : "metrics"
    }
    
    put_genomicsMetrics(RDB, formattedMetrics)
    
# libId: A string representing a BRI GenLIMS library ID
# fcId: A string representing a flow cell ID
# runId: A string representing a flow cell run ID
# projectId: A string of the form 'P###-##'
def processTenxSamples(
    libId,
    fcId,
    runId,
    projectId
):
    # sniff project/subproject
    superproject = projectId.split('-')[0]
    subproject = projectId.split('-')[1]
    
    sampleInfo = {
        "_id": libId + "_" + fcId,
        "projectId": superproject,
        "subprojectId": subproject,
        "dateCreated":  datetime.datetime.now(),
        "lastUpdated": datetime.datetime.now(),
        "runId": runId,
        "parentId": libId,
        "type": "sequenced tenx library"
    }
    put_genomicsSamples(RDB, sampleInfo)
    
# procDirPath: A string representing a path of the form:
# libOutPath: A string indicating the path to the processed library data outputs, relative to the 'root' directory
# libId: A string representing a BRI GenLIMS library ID
# fcId: A string representing a flow cell ID
# server: A string indicating the fileserver
# dataRoot: A string indicating the root path for flow cell run directories (includes mount point)
def processLibraryFiles(
    procDirPath,
    libId, 
    fcId, 
    libOutPath,
    dataRoot = "/mnt/bioinformatics/pipeline/Illumina/",
    server = "nfs.isilon01.brivmrc.org"
):
    # collect metadata 
    metadata = parseMetadata(libPath = os.path.join(procDirPath, libId))
    
    # set up common fields
    fileLocations = {
        "_id": libId + "_" + fcId,
        "server": server,
        "dataRoot": dataRoot,
        "libraryPath": libOutPath,
        "metadata": metadata,
        "dateCreated":  datetime.datetime.now(),
        "lastUpdated": datetime.datetime.now()
    }
    
    # check for files of interest and add to data to push
    dataPath = os.path.join(dataRoot, libOutPath) 
    dataFiles = os.listdir(dataPath)
    
    fileDict = {
        "web_summary.html": "webSummary",
        "consensus.bam": "alignments",
        "possorted_genome_bam.bam": "alignments",
        "vloupe.vloupe": "loupe",
        "cloupe.cloupe": "loupe",
        "metrics_summary.csv": "metrics",
        "all_contig.fastq": "fastq",
        "raw_feature_bc_matrix.h5": "counts",
        "molecule_info.h5": "moleculeInfo"
    }
    
    for currFile in fileDict.keys():
        if(currFile in dataFiles):
            fileLocations.update({fileDict[currFile] : currFile})
    
    put_genomicsFiles(RDB, fileLocations)
    

#====================
# Main program
#====================
@click.command()
@click.option('--quiet', 'verbosity', flag_value='quiet',
              help=("only display printed outputs in the console - "
                    "i.e., no log messages"))
@click.option('--debug', 'verbosity', flag_value='debug',
              help="include all debug log messages in the console")
@click.argument('path')
def main(verbosity, path):
    """
    Command line interface for the tenx utilities in bripipetools.
    """
    if verbosity == 'quiet':
        logger.setLevel(logging.ERROR)
    elif verbosity == 'debug':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    processTenxResults(path)
    

if __name__ == '__main__':
    main()
