import brigalaxy as bg
import sys, os, argparse, time, json, re

def printlog(string, file, msg=False):
    """This is a small custom function to combine print and write in one
       command."""
    if msg:
        msgFlag = "--> ".rjust(9)
        string = msgFlag + string

    print string
    file.write(string + "\n")

def load_users():
    with open('data/users.json') as f:
        users = json.load(f)
    return users

def load_params():
    with open('data/params.json') as f:
        params = json.load(f)
    return params

def parse_input_args(parser=None):
    users = load_users()
    user_list = [("%d [%s]" % (i, u)) for i, u in enumerate(users)]

    params = load_params()
    result_types = sorted(list(set(params['folders'].values())))
    result_list = [("%d [%s]" % (i, r)) for i, r in enumerate(result_types)]

    parser.add_argument('-f', '--flowcell',
                        required=True,
                        default=None,
                        help=("specify the flowcell associated with this "
                              "history - e.g., "
                              "150202_D00565_0080_AC5UCPANXX/"
                              "Project_Processed"))
    parser.add_argument('-p', '--project',
                        default=None,
                        help=("specify the tag/label for the project"
                              "associated with this history - i.e., "
                              "results will be stored in "
                              "<project>Processed folder"))
    parser.add_argument('-u', '--user_num',
                        type=int,
                        default=None,
                        nargs=1,
                        choices=range(len(users)),
                        help=("Select user: " +
                              ", ".join(user_list)))
    parser.add_argument('-d', '--root_directory',
                        default='/mnt/genomics/Illumina/',
                        help=("specify a non-default path to the flowcell "
                              "directory; default path is: "
                              "/mnt/genomics/Illumina/"))
    parser.add_argument('-x', '--exclude_results',
                        type=int,
                        default=None,
                        nargs='+',
                        choices=range(len(result_types)),
                        help=("Select one or more result types to exclude: " +
                              ", ".join(result_list)))

    # Parse and collect input arguments
    args = parser.parse_args()

    if len(args.exclude_results):
        exclude_results = [result_types[r] for r in args.exclude_results]

    return (args.flowcell, args.project, args.user_num, args.root_directory,
            exclude_results)

def get_output_labels(flowcell, project, history_name):

    if project is None:
        proj_re = re.compile('P+[0-9]+(-[0-9]+){,1}')
        try:
            project = proj_re.search(history_name).group()
            project_tag = 'Project_' + project + 'Processed'
        except:
            project = history_name
            project_tag = project + 'Processed'
    else:
        project_tag = project + 'Processed'

    date_tag = time.strftime("%y%m%d", time.gmtime())
    project_folder = project_tag + '_' + date_tag

    # Parse flow cell ID to create file tag
    try:
        fc_re = re.compile('((?<=(EXTERNAL_))|(?<=(_[A-B]))).*XX')
        fc_str = re.sub('EXTERNAL_[A-B]', 'EXTERNAL_', flowcell)
        flowcell_tag = fc_re.search(fc_str).group() + '_'
        file_tag = project + '_' + flowcell_tag + date_tag + '_'
    except:
        file_tag = project + '_multiFCs_' + date_tag + '_'

    return (project_folder, file_tag)


def main(argv):
    parser = argparse.ArgumentParser()
    fc,proj,user_num,root_dir,exclude = parse_input_args(parser)

    # Initialize session manager object for interacting with Galaxy API and
    # Galaxy server
    print "Connecting to Galaxy..."
    sm = bg.SessionManager(user_num=0, target_dir="outDir")

    # Initialize history manager object for collecting information about a
    # selected History
    print "Initializing History manager..."
    hm = bg.HistoryManager(sm.gi, history_id='bd9802014d926144')
    hname = hm.hname
    project_folder,file_tag = get_output_labels(fc, proj, hname)

    sm.add_target_dir(os.path.join(root_dir, project_folder))
    print sm.dir

    #
    #
    # # Get dataset graph for history
    # print "Building Dataset graph..."
    # dataset_graph = hm.show_dataset_graph()
    #
    # # Get list of input datasets
    # print "Identifying input Datasets..."
    # input_dataset_list = hm.show_input_datasets()
    #
    # print "Getting ouptut data..."
    # for i in input_dataset_list[0:1]:
    #
    #     rc = bg.ResultCollector(hm, dataset_graph, i)
    #     print "\nCollecting outputs for library:", rc.lib
    #     output_dataset_list = rc.show_output_list()
    #
    #     print "Downloading files..."
    #     for o in output_dataset_list:
    # #         print ResultDownloader(sm, rc.lib, o).show()
    #         rd = bg.ResultDownloader(sm, rc.lib, o)
    #         print " > Dataset:", rd.dname
    #         print " -- ", rd.go()
    # print "\nDone."

if __name__ == "__main__":
   main(sys.argv[1:])
