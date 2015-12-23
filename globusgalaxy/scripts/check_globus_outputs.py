import os, sys, re

class WorkflowParser(object):

    def __init__(self, batch_file=None):

        self.bf = batch_file
        self.read_batch_file()

    def read_batch_file(self):

        batch_file = self.bf
        with open(batch_file) as f:
            batch_lines = f.readlines()

        self.batch = batch_lines

    def get_params(self):

        param_line = [ l for l in self.batch if 'SampleName' in l ][0]
        param_dict = { idx: re.sub('##.*', '', p) \
                       for idx,p in enumerate(param_line.strip().split('\t')) }

        self.pd = param_dict

    def get_lib_params(self):

        if not hasattr(self, 'pd'):
            self.get_params()

        param_dict = self.pd
        lib_param_dict = [ { param_dict[i]: p \
                             for i,p in enumerate(l.strip().split('\t')) } \
                           for l in self.batch if re.search('lib[0-9]+', l) ]

        self.lpd = lib_param_dict

    def build_out_dict(self):

        if not hasattr(self, 'lpd'):
            self.get_lib_params()

        lib_param_dict = self.lpd
        out_file_dict = { pd['SampleName']: { re.sub('_out', '', k): pd[k] \
                                              for k in pd if 'out' in k } \
                          for pd in lib_param_dict }

        self.ofd = out_file_dict

    def show_output_files(self):

        if not hasattr(self, 'ofd'):
            self.build_out_dict()

        return self.ofd

class ResultCurator(object):
    def __init__(self, processed_dir=None):
        self.dir = processed_dir
        self.pf = re.search('Project_.*', processed_dir).group()

    def get_outputs(self):

        processed_dir = self.dir

        batch_file = [ f for f in os.listdir(processed_dir) if \
                       re.search('v[0-9]\.[0-9]+\.txt', f) ]

        if len(batch_file):
            batch_file = os.path.join(processed_dir, batch_file[0])

        output_dict = WorkflowParser(batch_file).show_output_files()

        self.od = output_dict

    def list_outputs(self):

        if not hasattr(self, 'od'):
            self.get_outputs()

        output_list = []
        for lib in self.od:
            output_list += [ re.sub('.*(?=genomics)', '', o) \
                             for o in self.od[lib].values() ]
        return output_list

    def curate_outputs(self):

        if not hasattr(self, 'od'):
            self.get_outputs()

        for lib in self.od:
            print lib
            sc = SampleCurator(lib, self.od[lib])
            sc.organize_files(self.dir)

def check_outputs(processed_dir):
    rc = ResultCurator(processed_dir)
    project_files = [ re.sub('.*(?=genomics)', '', os.path.join(dp, f)) \
                      for dp,dn,fn in os.walk(processed_dir) \
                      for f in fn ]
    file_sizes = [ os.stat(os.path.join(dp, f)).st_size \
                   for dp,dn,fn in os.walk(processed_dir) \
                   for f in fn ]

    project_files = [ re.sub('gProject', 'Project', f) for f in project_files ]
    project_files = [ re.sub('_backup', '', f) for f in project_files]
    missing_outputs = [ f for f in rc.list_outputs() \
                        if f not in project_files ]
    empty_outputs = [ f for idx,f in enumerate(project_files) \
                      if file_sizes[idx] is 0 ]

    return (missing_outputs, empty_outputs)

def main(argv):
    processed_dir = sys.argv[1]
    missing,empty = check_outputs(processed_dir)

    if len(missing):
        print "Missing output files:"
        for f in missing:
            print " %s" % f
    else:
        print "No missing outputs."

    if len(empty):
        print "\nEmpty output files:"
        for f in empty:
            print " %s" % f
    else:
        print "No empty outputs."

if __name__ == "__main__":
   main(sys.argv[1:])
