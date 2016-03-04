__author__ = 'jeddy'
import sys, os, re, argparse, time

"""generateBatchSubmitParams

This script is used to generate a batch submit file for Globus Genomics Galaxy,
with all parameters specified for the selected Workflow for each library
(sample).

Inputs:
    -u / --unalignedDir : directory with unaligned FASTQs from BaseSpace for
                          current project libraries; expected folder hierarchy
                          is as follows:

                          <flowcell-directory>/
                          |----Unaligned/
                               |----<project-directory> # aka "unalignedDir"
                                    |----<lib-directory>
                                         |----<fastq.gz-file-for-each-lane>
    -t / --workflowTemplate: empty batch submit file from Globus Genomics
                             Galaxy to be used as a template for specifying
                             parameters for the current project; each template
                             corresponds to a Workflow within Galaxy

Example:
    $ python generateBatchSubmitParams.py \
        -u /mnt/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/Unaligned/P43-12-23224208 \
        -t /mnt/genomics/galaxyWorkflows/Galaxy-API-Workflow-alignCount_truSeq_single_GRCh38_v1.txt
"""

### FUNCTIONS

# Parse flowcell folder from filepath part to get flowcell ID
def get_fc_tag(fcStr):
    fcStr = re.sub('EXTERNAL_[A-B]', 'EXTERNAL_', fcStr)
    fcRe = re.compile('((?<=(EXTERNAL_))|(?<=(_[A-B]))).*XX')
    fcTag = '_' + fcRe.search(fcStr).group()

    return fcTag

# Parse project folder from filepath part to get project ID
def get_proj(projStr):
    projRe = re.compile('P+[0-9]+(-[0-9]+){,1}')
    proj = projRe.search(projStr).group()

    return proj

# Break unaligned filepath into relevant parts and parse to get flowcell and
# project IDs
def parse_unaligned_path(unalignedDir):
    pathParts = re.split('/Unaligned/', unalignedDir)
    fcStr = re.split('/', pathParts[0])[-1]

    projStr = pathParts[-1]

    fcTag = get_fc_tag(fcStr)
    proj = get_proj(projStr)

    return (fcTag, proj)

def get_unique_keys(keys, idfun=None):
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in keys:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

# Parse workflow template to get keys for parameters as well as all other
# metadata/comment lines from the template file
def parse_workflow_template(batchWorkflowTemplate):
    templateLines = file(batchWorkflowTemplate).readlines()
    headerLine = [ line for line in templateLines if 'SampleName' in line ][0]
    headers = headerLine.rstrip('\t').split('\t')
    headerKeys = [ header.split('##')[0] for header in headers ]
    paramNames = [ header.split('::')[-1] for header in headers]
    laneOrder = [ re.search('[1-9]', p).group() \
                  for p in paramNames if re.search('from_path[1-8]', p) ]

    return get_unique_keys(headerKeys), laneOrder, templateLines

# Replace root directory with /~/ for compatibility with Globus transfer
def format_endpoint_dir(localDir):
    endpointDir = re.sub('.*(?=(/genomics))', '/~', localDir)

    return endpointDir

# Specify appropriate reference/annotation files for corresponding parameters
def build_ref_path(param, build = 'GRCh38'):
    refDict = {}
    refDict['GRCh38'] = dict([('gtf', 'Homo_sapiens.GRCh38.77.gtf'),
                              ('refflat', 'Homo_sapiens.GRCh38.77.refflat.txt'),
                              ('ribosomal_intervals',
                               'Homo_sapiens.GRCh38.77.ribosomalIntervalsWheaderV2.txt'),
                               ('adapters', 'smarter_adapter_seqs_3p_5p.fasta')])
    refType = re.sub('^annotation_', '', param)
    refPath = 'library::annotation::' + refDict[build].get(refType)

    return refPath

# Create label for processed output folder
def prep_output_directory(unalignedDir, proj):
    pathParts = re.split('/Unaligned/', unalignedDir)
    fcDir = pathParts[0]

    dateTag = time.strftime("%y%m%d", time.gmtime())

    targetDir = '%s/Project_%sProcessed_%s' % (fcDir, proj, dateTag)
    fastqDir = os.path.join(targetDir, 'inputFastqs')
    if not os.path.isdir(fastqDir):
        os.makedirs(fastqDir)

    return targetDir

# Create output subdirectories for each Workflow result type
def prep_output_subdir(targetDir, resultType):

    resultSubdir = os.path.join(targetDir, resultType)

    if not os.path.isdir(resultSubdir):
        os.makedirs(resultSubdir)

    return resultSubdir

# Parse library folder from filepath to get library ID (libID)
def parse_lib_path(libDir):
    libId = re.search('lib[0-9]+', libDir).group()

    return libId

# Get the location of the gzipped FASTQ file for the current lib and lane
def get_lane_fastq(libDir, lane):
    laneRe = re.compile('L00' + lane)
    laneFastq = [ os.path.join(libDir, fastq) \
                  for fastq in os.listdir(libDir) \
                  if laneRe.search(fastq) ]
    if len(laneFastq):
        laneFastq = laneFastq[0]
    # create empty file if no FASTQ exists for current lane
    else:
        emptyFastq = 'empty_L00' + lane + '.fastq.gz'
        laneFastq = os.path.join(libDir, emptyFastq)

        if not os.path.exists(laneFastq):
            open(laneFastq, 'a').close()

    return format_endpoint_dir(laneFastq)

# Create output file path corresponding to the current parameter / result type
def build_result_path(lib, targetDir, param):
    resultTypes = ['trimmed', 'counts', 'alignments', 'metrics',
                   'QC', 'Trinity', 'log']
    resultType = [ rType for rType in resultTypes \
                   if rType.lower() in param ][0]

    resultSubdir = prep_output_subdir(targetDir, resultType)

    outFile = re.sub('_out$', '', param)
    outFile = re.sub('_(?=([a-z]+$))', '.', outFile)
    outFile = lib + '_' + outFile

    resultPath = os.path.join(format_endpoint_dir(resultSubdir), outFile)

    return resultPath

# Fill in parameter values for current lib based on the keys from the template
def build_lib_param_list(lib, endpoint, targetDir, headerKeys, laneOrder, fcTag):
    libParams = []
    libId = parse_lib_path(lib)
    targetLib = libId + fcTag

    for param in headerKeys:
        if 'SampleName' in param:
            libParams.append(targetLib)
        elif 'fastq_in' in param:
            libParams.append(endpoint)
            for lane in laneOrder:
                libParams.append(get_lane_fastq(lib, lane))
        elif 'annotation' in param:
            refPath = build_ref_path(param)
            libParams.append(refPath)
        elif 'out' in param:
            if re.search('^fastq_out', param):
                finalFastq = '%s_R1-final.fastq.gz' % targetLib
                resultPath = os.path.join(format_endpoint_dir(targetDir),
                                          'inputFastqs', finalFastq)
            else:
                resultPath = build_result_path(targetLib, targetDir, param)
            libParams.append(endpoint)
            libParams.append(resultPath)

    return libParams

# Parse template and fill in appropriate parameter values for all project libs
def create_workflow_file(workflowTemplate, endpoint, unalignedDir, proj, fcTag):
    headerKeys,laneOrder,templateLines = parse_workflow_template(workflowTemplate)
    workflowLines = templateLines

    projLineNum = [ idx for idx,line in enumerate(templateLines) \
                    if 'Project Name' in line ][0]
    workflowLines[projLineNum] = re.sub('<Your_project_name>', proj,
                                        templateLines[projLineNum])
    workflowLines[-1] = re.sub('\t$', '\n', workflowLines[-1])

    unalignedLibs = [ os.path.join(unalignedDir, entry) \
                      for entry in os.listdir(unalignedDir) \
                      if os.path.isdir(os.path.join(unalignedDir, entry)) ]

    # temp kluge to select just one lib
    unalignedLibs = [ lib for lib in unalignedLibs if re.search('lib6(830|922)', lib) ] # for P43-12
    # unalignedLibs = [ lib for lib in unalignedLibs if re.search('lib66(05|20)', lib) ] # for P109-1

    targetDir = prep_output_directory(unalignedDir, proj)

    for lib in unalignedLibs:
        if "Undetermined" not in lib:
            libParams = build_lib_param_list(lib, endpoint, targetDir,
                                             headerKeys, laneOrder, fcTag)
            workflowLines.append(('\t').join(libParams) + '\n')

    return (workflowLines, targetDir)

# Write completed batch workflow to file and return formatted path
def write_batch_workflow(workflowLines, targetDir, workflowTemplate, proj):
    templateFile = os.path.basename(workflowTemplate)
    workflowFile = proj + '_' + templateFile
    workflowPath = os.path.join(targetDir, workflowFile)

    wFile = open(workflowPath, 'w')
    wFile.writelines(workflowLines)
    wFile.close()

    print "Batch file path: " + format_endpoint_dir(workflowPath)

# Parse input arguments and call above functions to generate batch submit file
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--endpoint',
                        required=True,
                        default=None,
                        help=("specify the Globus Online endpoint "
                              "where input data is stored / results are "
                              "to be saved - e.g., "
                              "jeddy#srvgridftp01"))
    parser.add_argument('-u', '--unalignedDir',
                        required=True,
                        default=None,
                        help=("specify the directory of unaligned library "
                              "FASTQs to be processed - e.g., "
                              "/mnt/genomics/Illumina/"
                              "150615_D00565_0087_AC6VG0ANXX/Unaligned"
                              "P43-12-23224208"))
    parser.add_argument('-t', '--workflowTemplate',
                        default=None,
                        help=("specify batch submission template "
                              "for the Galaxy Workflow to be used for"
                              "processing the current project - e.g., "
                              "/mnt/genomics/galaxyWorkflows/"
                              "Galaxy-API-Workflow-alignCount_truSeq_"
                              "single_GRCh38_v1.txt"))
    args = parser.parse_args()

    endpoint = args.endpoint
    unalignedDir = args.unalignedDir
    workflowTemplate = args.workflowTemplate

    unalignedDir = os.path.abspath(unalignedDir)
    fcTag,proj = parse_unaligned_path(unalignedDir)

    workflowLines,targetDir = create_workflow_file(workflowTemplate, endpoint,
                                                   unalignedDir, proj, fcTag)
    write_batch_workflow(workflowLines, targetDir,
                         workflowTemplate, proj)

if __name__ == "__main__":
   main(sys.argv[1:])
