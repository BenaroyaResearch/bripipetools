
import sys, os, re, argparse

def get_input_list(inputDir):
    inputLibs = [ os.path.join(dp, f) \
                  for dp,dn,fn in os.walk(inputDir) \
                  for f in fn if re.search('.*fast.*$', f) ]
    return inputLibs

def get_lib_base(filePath):
    libBase = re.search('.*(lib|SRR)[0-9]+', filePath).group()
    return libBase

def build_mixcr_cmd(inLib, resultsDir, region = "full"):
    libBase = get_lib_base(inLib)
    fileBase = os.path.basename(libBase)
    libBase = os.path.join(resultsDir, fileBase)
    mixcrOut = libBase + '_mixcrReport.txt'
    outClns = libBase + '_mixcrClns.txt'
    outPretty = libBase + '_mixcrAlignPretty.txt'
    tempVdjca = libBase + '_mixcrAlign.vdjca'
    tempClns = libBase + '_mixcrAssemble.clns'

    # Old version: `-l` (locus) flag deprecated, replaced with
    # `-c` (chain) flag after version 2.0
    #alignCmd = ("mixcr align -l TCR -r %s %s %s" %
    #            (mixcrOut, inLib, tempVdjca))
    
    # align to and produce sequence for entire chain
    if region == "full":
        alignCmd = ("mixcr align -c TCR -OvParameters.geneFeatureToAlign=VTranscript -r %s %s %s" %
                   (mixcrOut, inLib, tempVdjca))
        assembleCmd = ("mixcr assemble -OassemblingFeatures=VDJRegion -r %s %s %s" %
                      (mixcrOut, tempVdjca, tempClns))
    # align to and produce sequence for only CDR3 region              
    elif region == "CDR3":
        alignCmd = ("mixcr align -c TCR -r %s %s %s" %
                    (mixcrOut, inLib, tempVdjca))
        assembleCmd = ("mixcr assemble -r %s %s %s" %
                       (mixcrOut, tempVdjca, tempClns))
                       
    exportCmd = ("mixcr exportClones %s %s" %
                 (tempClns, outClns))
    exportPrettyCmd = ("mixcr exportAlignmentsPretty %s %s" %
                       (tempVdjca, outPretty))
    mixcrCmd = ('\n').join([alignCmd, assembleCmd, exportCmd, exportPrettyCmd])
    return mixcrCmd

def build_slurm_cmd(mixcrCmd, excludeNodes):
    if(excludeNodes != None):
        sbatchCmd = 'sbatch -x' + excludeNodes + '-N 1 --exclusive -J runMixcr.py -o slurm.out --open-mode=append <<EOF\n#!/bin/bash'
    else:
        sbatchCmd = 'sbatch -N 1 --exclusive -J runMixcr.py -o slurm.out --open-mode=append <<EOF\n#!/bin/bash'
    
    cmdList = [sbatchCmd, mixcrCmd, 'EOF']
    slurmCmd = ('\n').join(cmdList)
    return slurmCmd

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputDir',
                        required=True,
                        default=None,
                        help=("path to input FASTQ directory"))
    parser.add_argument('-o', '--resultsDir',
                        required=True,
                        default=None,
                        help=("path to output results direcotry"))
    parser.add_argument('-x', '--excludeNodes',
                        required=False,
                        default=None,
                        help=("comma-separated SLURM node(s) to exclude"))
    # parser.add_argument('-s', '--sourceType,
    #                     required=False,
    #                     nargs=1,
    #                     choices=['f', 't'],
    #                     default='f',
    #                     help=("[f] adapter & quality trimmed FASTQs, "
    #                           "[t] Trinity assembled FASTAs"))

    # Parse and collect input arguments
    args = parser.parse_args()

    # Specify inputs
    inputDir = os.path.abspath(args.inputDir)
    resultsDir = os.path.join(os.path.dirname(inputDir), args.resultsDir)
    excludeNodes = args.excludeNodes
    # sourceType = args.sourceType

    if not os.path.isdir(resultsDir):
        os.mkdir(resultsDir)

    inputLibs = get_input_list(inputDir)

    for inLib in inputLibs:
        mixcrCmd = build_mixcr_cmd(inLib, resultsDir)
        slurmCmd = build_slurm_cmd(mixcrCmd, excludeNodes)
        os.system(slurmCmd)
        print slurmCmd + '\n'

if __name__ == "__main__":
   main(sys.argv[1:])
