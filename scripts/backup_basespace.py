import os, sys, re
import subprocess
import pipes

def list_project_dirs(mount_path):
    mount_project_dir = os.path.join(mount_path, 'Projects')
    return [os.path.join(mount_project_dir, d) 
            for d in os.listdir(mount_project_dir)
            if (os.path.isdir(os.path.join(mount_project_dir, d))
                and not re.search('Unindexed', d)
                and not re.search('^\.', d)
                and not re.search('-0', d))]

def get_project_app_dir(project_path):
    app_session_dir = os.path.join(project_path, 'AppSessions')
    return [os.path.join(app_session_dir, d) 
            for d in os.listdir(app_session_dir)
            if os.path.isdir(os.path.join(app_session_dir, d))
            and not re.search('^\.', d)
            and re.search('fastq', d.lower())][-1]

def get_app_props_dir(app_path):
    return(os.path.join(app_path, 'Properties'))

def get_app_logs_dir(app_path):
    app_logs_dir = os.path.join(app_path, 'Logs')
    if 'data' in os.listdir(app_logs_dir):
        app_input_dir = os.path.join(app_logs_dir, 'data', 'input')
        return [os.path.join(app_input_dir, d)
                for d in os.listdir(app_input_dir)
                if os.path.isdir(os.path.join(app_input_dir, d))
                and not re.search('^\.', d)][0]
    else:
        return app_logs_dir

def sniff_sample_sheet(app_logs_path):
    sample_sheet_file = [os.path.join(app_logs_path, f) 
                         for f in os.listdir(app_logs_path)
                         if re.search('^SampleSheet', f)][0]
    with open(sample_sheet_file) as f:
        while True:
            ss_line = f.readline()
            if re.search('experimentname', re.sub(' ', '', ss_line).lower()):
                return ss_line.rstrip().split('_')[1]
            pass

def copy_data(flowcell_path, app_logs_path, app_props_path):
    if os.path.isdir(flowcell_path):
        print(' - Flowcell folder {} already exists; skipping.'.format(flowcell_path))
    else:
        target_logs_path = os.path.join(flowcell_path, 'logs')
        os.makedirs(target_logs_path)
        print(' - Copying log data from {} to {}...'.format(app_logs_path,
                                                            target_logs_path))
        log_copy_cmd = 'rsync -r {} {}'.format(pipes.quote(app_logs_path + '/'), 
                                            target_logs_path)
        subprocess.Popen(log_copy_cmd, shell=True)

        target_props_path = os.path.join(flowcell_path, 'properties')
        os.makedirs(target_props_path)
        print(' - Copying property data from {} to {}...'.format(app_props_path,
                                                                 target_props_path))

        props_copy_cmd = 'rsync -r {} {}'.format(pipes.quote(app_props_path + '/'),
                                                 target_props_path)
        subprocess.Popen(props_copy_cmd, shell=True)

def backup_project(project_path, target_path):
    app_logs_dir = get_app_logs_dir(get_project_app_dir(project_path))
    app_props_dir = get_app_props_dir(get_project_app_dir(project_path))
    project_flowcell = sniff_sample_sheet(app_logs_dir)
    flowcell_path = os.path.join(target_path, project_flowcell)
    copy_data(flowcell_path, app_logs_dir, app_props_dir)

def main(argv):
    bs_mount_dir = sys.argv[1]
    backup_dir = sys.argv[2]

    project_dirs = list_project_dirs(bs_mount_dir)
    for idx,p in enumerate(project_dirs):
        print('\n[{} / {}] Backing up project data in {}'.format(idx + 1, len(project_dirs), p))
        backup_project(p, backup_dir)

if __name__ == "__main__":
    main(sys.argv[1:])
