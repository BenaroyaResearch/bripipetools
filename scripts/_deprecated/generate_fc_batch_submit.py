__author__ = 'jeddy'
import sys, os, re, argparse, time

"""generate_fc_batch_submit

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
def get_fc_tag(fc_str):
    fc_str = re.sub('EXTERNAL_[A-B]', 'EXTERNAL_', fc_str)
    fc_re = re.compile('((?<=(EXTERNAL_))|(?<=(_[A-B]))).*X[X|Y]')
    try:
        fc_tag = '_' + fc_re.search(fc_str).group()
        return fc_tag
    except AttributeError:
        return ''

# Parse project folder from filepath part to get project ID
def get_proj(proj_str):
    proj_re = re.compile('P+[0-9]+(-[0-9]+){,1}')
    try:
        proj = proj_re.search(proj_str).group()
        return proj
    except AttributeError:
        return proj_str

# Break unaligned filepath into relevant parts and parse to get flowcell and
# project IDs
def parse_unaligned_path(unaligned_dir):
    path_parts = re.split('/Unaligned/', unaligned_dir)
    fc_str = re.split('/', path_parts[0])[-1]

    proj_str = path_parts[-1]

    fc_tag = get_fc_tag(fc_str)
    proj = get_proj(proj_str)

    return (fc_tag, proj)

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
def parse_workflow_template(batch_workflow_template):
    template_lines = file(batch_workflow_template).readlines()
    header_line = [line for line in template_lines if 'SampleName' in line][0]
    headers = header_line.rstrip('\t').split('\t')
    header_keys = [header.split('##')[0] for header in headers]
    param_names = [header.split('::')[-1] for header in headers]
    lane_order = [re.search('[1-9]', p).group() \
                  for p in param_names if re.search('from_path[1-8]', p) ]

    return get_unique_keys(header_keys), lane_order, template_lines

# Replace root directory with /~/ for compatibility with Globus transfer
def format_endpoint_dir(local_dir):
    # endpoint_dir = re.sub('.*(?=(/genomics))', '/~', local_dir)
    endpoint_dir = re.sub('.*(?=(/genomics))', '/mnt', local_dir)

    return endpoint_dir

# Specify appropriate reference/annotation files for corresponding parameters
def build_ref_path(param, build = 'GRCh38'):
    ref_dict = {}
    ref_dict['GRCh38'] = dict([('gtf', 'GRCh38/Homo_sapiens.GRCh38.77.gtf'),
                               ('refflat', 'GRCh38/Homo_sapiens.GRCh38.77.refflat.txt'),
                               ('ribosomal_intervals',
                                'GRCh38/Homo_sapiens.GRCh38.77.ribosomalIntervalsWheader_reorder.txt'),
                               ('adapters', 'adapters/smarter_adapter_seqs_3p_5p.fasta')])
    ref_dict['NCBIM37'] = dict([('gtf', 'NCBIM37/Mus_musculus.NCBIM37.67.gtf'),
                                ('refflat', 'NCBIM37/Mus_musculus.NCBIM37.67.refflat.txt'),
                                ('ribosomal_intervals',
                                'NCBIM37/Mus_musculus.NCBIM37.67.ribosomalIntervalsWheader_reorder.txt'),
                                ('adapters', 'adapters/smarter_adapter_seqs_3p_5p.fasta')])
    ref_type = re.sub('^annotation_', '', param)
    ref_path = 'library::annotation::' + ref_dict[build].get(ref_type)

    return ref_path

# Create label for processed output folder
def prep_output_directory(unaligned_dir, proj):
    path_parts = re.split('/Unaligned/', unaligned_dir)
    fc_dir = path_parts[0]

    date_tag = time.strftime("%y%m%d", time.gmtime())

    target_dir = '%s/Project_%sProcessed_globus_%s' % (fc_dir, proj, date_tag)
    fastq_dir = os.path.join(target_dir, 'inputFastqs')
    if not os.path.isdir(fastq_dir):
        os.makedirs(fastq_dir)

    return (target_dir, date_tag)

# Create output subdirectories for each Workflow result type
def prep_output_subdir(target_dir, result_type):

    result_subdir = os.path.join(target_dir, result_type)

    if not os.path.isdir(result_subdir):
        os.makedirs(result_subdir)

    return result_subdir

# Parse library folder from filepath to get library ID (libID)
def parse_lib_path(lib_dir):
    try:
        lib_id = re.search('lib[0-9]+', lib_dir).group()
        return lib_id
    except AttributeError:
        return re.search('Sample_.*[0-9]+', lib_dir).group()

# Get the location of the gzipped FASTQ file for the current lib and lane
def get_lane_fastq(lib_dir, lane):
    lane_re = re.compile('L00' + lane)
    lane_fastq = [os.path.join(lib_dir, fastq)
                  for fastq in os.listdir(lib_dir)
                  if lane_re.search(fastq)]
    if len(lane_fastq):
        lane_fastq = lane_fastq[0]
    # create empty file if no FASTQ exists for current lane
    else:
        empty_fastq = 'empty_L00' + lane + '.fastq.gz'
        lane_fastq = os.path.join(lib_dir, empty_fastq)

        if not os.path.exists(lane_fastq):
            open(lane_fastq, 'a').close()

    return format_endpoint_dir(lane_fastq)

# Create output file path corresponding to the current parameter / result type
def build_result_path(lib, target_dir, param):
    result_types = ['trimmed', 'counts', 'alignments', 'metrics',
                   'QC', 'Trinity', 'log']
    result_type = [r_type for r_type in result_types
                   if r_type.lower() in param][0]

    result_subdir = prep_output_subdir(target_dir, result_type)

    out_file = re.sub('_out$', '', param)
    out_file = re.sub('_(?=([a-z]+$))', '.', out_file)
    out_file = lib + '_' + out_file

    result_path = os.path.join(format_endpoint_dir(result_subdir), out_file)

    return result_path

# Fill in parameter values for current lib based on the keys from the template
def build_lib_param_list(lib, endpoint, target_dir, header_keys, lane_order, fc_tag, build='GRCh38'):
    lib_params = []
    lib_id = parse_lib_path(lib)
    target_lib = lib_id + fc_tag

    for param in header_keys:
        if 'SampleName' in param:
            lib_params.append(target_lib)
        elif 'fastq_in' in param:
            lib_params.append(endpoint)
            for lane in lane_order:
                lib_params.append(get_lane_fastq(lib, lane))
        elif 'annotation' in param:
            ref_path = build_ref_path(param, build)
            lib_params.append(ref_path)
        elif 'out' in param:
            if re.search('^fastq_out', param):
                final_fastq = '%s_R1-final.fastq.gz' % target_lib
                result_path = os.path.join(format_endpoint_dir(target_dir),
                                          'inputFastqs', final_fastq)
            else:
                result_path = build_result_path(target_lib, target_dir, param)
            lib_params.append(endpoint)
            lib_params.append(result_path)

    return lib_params


def get_project_params(endpoint, header_keys, lane_order, unaligned_dir,
                       project_lines=None, N=None, sort=False, build='GRCh38'):
    if project_lines is None:
        project_lines = []

    fc_tag,proj = parse_unaligned_path(unaligned_dir)

    unaligned_libs = [os.path.join(unaligned_dir, entry)
                      for entry in os.listdir(unaligned_dir)
                      if os.path.isdir(os.path.join(unaligned_dir, entry))]

    # temp kluge to select just one lib
    # unaligned_libs = [ lib for lib in unaligned_libs if re.search('lib6(830|922)', lib) ] # for P43-12
    # unaligned_libs = [ lib for lib in unaligned_libs if re.search('lib6(830|822|605)', lib) ] # for P43-12/13 or P109-1
    # unaligned_libs = [ lib for lib in unaligned_libs if re.search('lib(9497|9555)', lib) ] # for P43-12/13 or P109-1
    # unalignedLibs = [ lib for lib in unalignedLibs if re.search('lib66(05|20)', lib) ] # for P109-1

    if sort:
        unaligned_libs = sorted(unaligned_libs,
                                key=lambda x: sum(os.path.getsize(os.path.join(x, f))
                                                  for f in os.listdir(x)))

    if N is not None:
        unaligned_libs = unaligned_libs[0:N] # first N libs, any project

    target_dir,date_tag = prep_output_directory(unaligned_dir, proj)

    for lib in unaligned_libs:
        if "Undetermined" not in lib:
            lib_params = build_lib_param_list(lib, endpoint, target_dir,
                                              header_keys, lane_order, fc_tag,
                                              build)
            project_lines.append(('\t').join(lib_params) + '\n')

    return (proj, fc_tag, project_lines, date_tag)


# Parse template and fill in appropriate parameter values for all project libs
def create_workflow_file(endpoint, workflow_template, project_list, N=None, sort=False):
    header_keys,lane_order,template_lines = parse_workflow_template(workflow_template)
    workflow_lines = template_lines
    workflow_lines[-1] = re.sub('\t$', '\n', workflow_lines[-1])

    builds = ['GRCh38', 'NCBIM37']
    build = [b for b in builds if re.search(b.lower(), workflow_template)][0]

    proj_list = []
    for unaligned_project in project_list:
        proj,fc_tag,proj_lines,date_tag = get_project_params(endpoint, header_keys,
                                                             lane_order, unaligned_project,
                                                             N=N, sort=sort, build=build)
        proj_list.append(proj)
        workflow_lines += proj_lines

    submit_tag = '%s_%s%s' % (date_tag, ('_').join(proj_list), fc_tag)
    proj_line_num = [idx for idx,line in enumerate(template_lines)
                    if 'Project Name' in line][0]
    workflow_lines[proj_line_num] = re.sub('<Your_project_name>', submit_tag,
                                           template_lines[proj_line_num])

    return (workflow_lines, submit_tag)

# Write completed batch workflow to file and return formatted path
def write_batch_workflow(workflow_lines, flowcell_dir, workflow_template, submit_tag):

    target_dir = os.path.join(flowcell_dir, 'globus_batch_submission')
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    template_file = os.path.basename(workflow_template)
    workflow_file = submit_tag + '_' + template_file
    workflow_path = os.path.join(target_dir, workflow_file)

    w_file = open(workflow_path, 'w+')
    w_file.writelines(workflow_lines)
    w_file.close()

    print "Batch file path: \n%s" % format_endpoint_dir(workflow_path)

# Prompt user to specify workflow for each flowcell project
def build_submit_dict(flowcell_dir, workflow_dir, optimized_only=False):

    flowcell_projects = [os.path.join(flowcell_dir, 'Unaligned', p)
                     for p in os.listdir(os.path.join(flowcell_dir, 'Unaligned'))
                     if '.' not in p]
    flowcell_projects.sort()

    workflow_choices = [os.path.join(workflow_dir, f)
                        for f in os.listdir(workflow_dir)
                        if 'Galaxy-API' not in f]
    workflow_choices.sort()

    if optimized_only:
        workflow_choices = [f for f in workflow_choices
                            if re.search('optimized', f)]

    ps_cont = True
    submit_dict = {}
    while ps_cont:
        print(submit_dict)
        print "\nFound the following projects: [current workflows selected]"
        for i, p in enumerate(flowcell_projects):
            workflow_nums = [w for w, k in enumerate(workflow_choices)
                             if p in submit_dict.get(k, [])]
            print "%3d : %s %s" % (i, os.path.basename(p), str(workflow_nums))

        p_i = raw_input("\nType the number of the project you wish to select or hit enter to finish: ")

        if len(p_i):
            selected_project = flowcell_projects[int(p_i)]

            for j, w in enumerate(workflow_choices):
                print "%3d : %s" % (j, os.path.basename(w))
            w_j = raw_input("\nSelect the number of the workflow to use for project %s: "
                            % os.path.basename(selected_project))
            selected_workflow = workflow_choices[int(w_j)]

            submit_dict.setdefault(selected_workflow, []).append(selected_project)
        else:
            ps_cont = False

    return submit_dict

# Parse input arguments and call above functions to generate batch submit file
def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--endpoint',
                        required=True,
                        default=None,
                        help=("specify the Globus Online endpoint "
                              "where input data is stored / results are "
                              "to be saved - e.g., "
                              "benaroyaresearch#BRIGridFTP"))
    parser.add_argument('-f', '--flowcell_dir',
                        required=True,
                        default=None,
                        help=("specify the directory of unaligned library "
                              "FASTQs to be processed - e.g., "
                              "/mnt/genomics/Illumina/"
                              "150615_D00565_0087_AC6VG0ANXX/Unaligned"
                              "P43-12-23224208"))
    parser.add_argument('-w', '--workflow_dir',
                        default=None,
                        help=("specify batch submission template "
                              "for the Galaxy Workflow to be used for"
                              "processing the current project - e.g., "
                              "/mnt/genomics/galaxyWorkflows/"
                              "Galaxy-API-Workflow-alignCount_truSeq_"
                              "single_GRCh38_v1.txt"))
    parser.add_argument('-N', '--first_N',
                        type=int,
                        default=None),
    parser.add_argument('-s', '--sort_libs',
                        action='store_true',
                        help=("sort libraries from smallest to largest"))
    parser.add_argument('-o', '--optimized_only',
                        action='store_true',
                        help=("show only optimized workflows"))
    args = parser.parse_args()

    endpoint = args.endpoint
    flowcell_dir = args.flowcell_dir
    workflow_dir = args.workflow_dir
    N = args.first_N
    sort_libs = args.sort_libs
    optimized_only = args.optimized_only

    submit_dict = build_submit_dict(flowcell_dir, workflow_dir, optimized_only)

    for w in submit_dict:
        workflow_lines,submit_tag = create_workflow_file(endpoint,
                                                         w, submit_dict[w],
                                                         N, sort_libs)
        write_batch_workflow(workflow_lines, flowcell_dir, w, submit_tag)

if __name__ == "__main__":
   main(sys.argv[1:])
