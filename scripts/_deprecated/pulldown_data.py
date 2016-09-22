import _mypath
import sys, os, argparse, time, json, re
from bripipetools import brigalaxy as bg

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
                        default=[],
                        nargs='+',
                        choices=range(len(result_types)),
                        help=("Select one or more result types to exclude: " +
                              ", ".join(result_list)))

    # Parse and collect input arguments
    args = parser.parse_args()

    results_dict = {}
    for i,r in enumerate(result_types):
        results_dict[r] = i not in args.exclude_results

    return (args.flowcell, args.project, args.user_num, args.root_directory,
            results_dict)

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

    return (project, project_folder, file_tag)

def initialize_log(session_manager, history_name, project, file_tag):
    # Create log file and begin logging
    outlog = os.path.join(session_manager.dir, file_tag + 'pulldown_log.txt')
    log = open(outlog, 'w')

    # Get current time
    current_time = time.asctime(time.gmtime())

    # Get system user name
    sys_user = os.getlogin()

    printlog(("Script run by user %s on %s" % (sys_user, current_time)), log)

    printlog(("\nConnected to Galaxy server at %s as user %s") %
             (session_manager.server, session_manager.user['username']), log)

    # Print and log script settings
    printlog("\n### SCRIPT SETTINGS ###", log)

    printlog(("\nSelected history: '%s'" % history_name), log)
    printlog(("Project ID/label: '%s'" % project), log, msg=True)
    printlog(("\nPath to flowcell & results: %s" % (session_manager.dir)), log)
    printlog(("Combined count/metric files will be prepended with '%s' tag" %
              file_tag), log)

    printlog("\nCollecting the following result types (if available):", log)
    [ printlog(("  > %s : %s" % (r, session_manager.rd[r])), log) \
      for r in session_manager.rd ]

    return log

def main(argv):
    parser = argparse.ArgumentParser()
    fc,proj,user_num,root_dir,results_dict = parse_input_args(parser)

    # Initialize session manager object for interacting with Galaxy API and
    # Galaxy server
    print "(Connecting to Galaxy...)"
    sm = bg.SessionManager(include_results=results_dict)

    # Initialize history manager object for collecting information about a
    # selected History
    print "(Initializing History manager...)"
    hm = bg.HistoryManager(sm.gi)
    hname = hm.hname
    proj,project_folder,file_tag = get_output_labels(fc, proj, hname)

    sm.add_target_dir(os.path.join(root_dir, fc, project_folder))

    print "(Initializing pulldown log...)\n"
    log = initialize_log(sm, hname, proj, file_tag)

    # Get list of input datasets
    print "\n(Identifying input Datasets...)"
    hm.collect_history_info()
    input_dataset_list = hm.show_input_datasets()

    printlog("\n### DATA PULLDOWN ###\n", log)
    print "(Getting ouptut data...)"
    for i in input_dataset_list:

        rc = bg.ResultCollector(hm, i)
        printlog("\nCollecting outputs for library: %s" % rc.lib, log)
        output_dataset_list = rc.show_output_list()

        print "(Downloading files...)"
        for idx,o in enumerate(output_dataset_list):
            rd = bg.ResultDownloader(sm, rc.lib, o)

            printlog("%4d (hid): %s [from %s]" % (idx, rd.label, rd.prior), log)
            [printlog(m, log, msg=True) for m in rd.go()]
    print "\nDone."
    log.close()

if __name__ == "__main__":
   main(sys.argv[1:])
