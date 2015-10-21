import brigalaxy as bg
import sys, os, argparse, re

def parse_input_args(parser=None):
    parser.add_argument('-d', '--processedDir',
                        required=True,
                        default=None,
                        help=("path to processed directory - e.g., "
                              "/mnt/genomics/Illumina/"
                              "150218_D00565_0081_BC5UF5ANXX/"
                              "Project_P69Processed"))
    parser.add_argument('-r', '--resultType',
                        default=None,
                        choices=['c', 'm', 'b'],
                        help=("Select type of result file to combine: " +
                              "c [counts], m [metrics], b [both]"))
    parser.add_argument('-t', '--fileTag',
                        default='',
                        help=("specify tag to add to combined files - e.g., "
                              "<tag>_combined_counts.csv"))

    # Parse and collect input arguments
    args = parser.parse_args()

    processedDir = os.path.abspath(args.processedDir)
    return (processedDir, args.resultType, args.fileTag)

def get_file_tag(project_folder):
    path_parts = os.path.split(project_folder)
    project_folder = path_parts[-1]
    flowcell = os.path.basename(path_parts[0])

    # Parse flow cell ID to create file tag
    try:
        fc_re = re.compile('((?<=(EXTERNAL_))|(?<=(_[A-B]))).*XX')
        fc_str = re.sub('EXTERNAL_[A-B]', 'EXTERNAL_', flowcell)
        flowcell_tag = '_' + fc_re.search(fc_str).group()
    except:
        flowcell_tag = '_multiFCs'

    file_tag = re.sub('Project_', '', project_folder)
    file_tag = re.sub('Processed', flowcell_tag, file_tag)

    print "\nSuggested file tag name: " + file_tag
    enterName = raw_input("Use suggested tag (selecting 'n' will leave tag empty)? (y/[n]) ")
    if enterName is 'y':
        return file_tag + '_'
    else:
        return ''

def main(argv):
    parser = argparse.ArgumentParser()
    project_folder,rt,file_tag = parse_input_args(parser)


    if len(file_tag) > 0:
        file_tag = file_tag + '_'
    else:
        file_tag = get_file_tag(project_folder)

    if rt == 'c' or rt == 'b':
        countRs = bg.ResultStitcher('counts', project_folder)
        fileName = file_tag + 'combined_counts.csv'
        countsFile = os.path.join(countRs.resultDir, fileName)
        countRs.execute(countsFile)

    if rt == 'm' or rt == 'b':
        metricRs = bg.ResultStitcher('metrics', project_folder)
        fileName = file_tag + 'combined_metrics.csv'
        metricsFile = os.path.join(metricRs.resultDir, fileName)
        metricRs.execute(metricsFile)

if __name__ == "__main__":
   main(sys.argv[1:])
