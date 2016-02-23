import sys, os, re, argparse, csv
import shutil

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

        param_line = [l for l in self.batch if 'SampleName' in l][0]
        param_dict = {idx: re.sub('##.*', '', p) \
                      for idx,p in enumerate(param_line.strip().split('\t'))}

        self.pd = param_dict

    def get_lib_params(self):

        if not hasattr(self, 'pd'):
            self.get_params()

        param_dict = self.pd
        lib_param_dict = [{param_dict[i]: p \
                           for i,p in enumerate(l.strip().split('\t'))} \
                          for l in self.batch if re.search('lib[0-9]+', l)]

        self.lpd = lib_param_dict

    def build_out_dict(self):

        if not hasattr(self, 'lpd'):
            self.get_lib_params()

        lib_param_dict = self.lpd
        out_file_dict = {pd['SampleName']: {re.sub('_out', '', k): pd[k] \
                                            for k in pd if 'out' in k} \
                         for pd in lib_param_dict}

        self.ofd = out_file_dict

    def show_output_files(self):

        if not hasattr(self, 'ofd'):
            self.build_out_dict()

        return self.ofd

class CompileController(object):

    def __init__(self, flowcell_dir=None):
        self.fc_dir = flowcell_dir

    def select_batch(self):
        batch_submit_dir = os.path.join(self.fc_dir, "globus_batch_submission")
        batch_dates = list(set(f.split('_')[0] for f in os.listdir(batch_submit_dir)))

        print "\nFound the following Globus Genomics Galaxy batches:"
        for i, d in enumerate(batch_dates):
            print "%3d : %s" % (i, d)
        batch_i = raw_input("Select the date of flowcell batch to compile: ")
        batch_date = batch_dates[int(batch_i)]

        self.batch_submit_files = [os.path.join(batch_submit_dir, f)
                                   for f in os.listdir(batch_submit_dir)
                                   if f.split('_')[0] in batch_date]

    def go(self):

        if not hasattr(self, 'batch_submit_files'):
            self.select_batch()

        for f in self.batch_submit_files:
            rc = ResultCurator(self.fc_dir, f).curate_outputs()

class ResultCurator(object):

    def __init__(self, flowcell_dir=None, batch_submit_file=None):
        self.fc_dir = flowcell_dir
        self.submit_file = batch_submit_file
        self.get_workflow()

    def get_workflow(self):

        batch_workflow = re.search('(?<=optimized_).*(?=.txt)',
                                   self.submit_file).group()
        self.workflow = batch_workflow

    def get_outputs(self):

        output_dict = WorkflowParser(self.submit_file).show_output_files()

        self.od = output_dict

    def get_project_dir(self, lib=None):

        project_dir = os.path.join(self.fc_dir,
                                   re.search('Project_[^/]*',
                                             self.od[lib].get('workflow_log_txt')).group())
        return project_dir

    def curate_outputs(self):

        if not hasattr(self, 'od'):
            self.get_outputs()

        for idx,lib in enumerate(self.od):
            project_dir = self.get_project_dir(lib)
            proj_id = re.search('P+[0-9]+(-[0-9]+){,1}', project_dir).group()
            print "\nWorkflow: %s" % self.workflow
            print (">> Compiling outputs for %s [%s] (%d of %d)\n" %
                   (lib, proj_id, idx + 1, len(self.od)))
            sc = SampleCurator(lib, self.od[lib])
            sc.organize_files(self.get_project_dir(lib))

class SampleCurator(object):

    def __init__(self, lib_id=None, output_dict=None):

        self.lib = lib_id
        self.lod = output_dict

    def get_result_type(self, output):
        output_str = re.sub('_[a-z]+$', '', output)
        output_type = re.search('(?<=_)[a-z]+$', output_str)
        if output_type:
            result_type = output_type.group()
        else:
            result_type = output_str

        return result_type

    def get_result_source(self, output):
        if not re.search('fastq$', output):
            result_sources = ['picard_align', 'picard_markdups', 'picard_rnaseq',
                              'htseq', 'trinity', 'tophat', 'tophat_stats', 'fastqc',
                              'workflow_log']
            result_source = [ rs for rs in result_sources \
                              if re.search(rs.lower(), output) ][0]
        else:
            result_sources = ['fastq', 'trimmed_fastq']
            result_source = [ rs for rs in result_sources \
                              if re.search('^' + rs.lower() + '$', output) ][0]

        return result_source

    def build_source_dict(self):

        output_dict = self.lod

        source_dict = {}

        for o in output_dict:
            rt = self.get_result_type(o)
            rs = self.get_result_source(o)

            if rs in source_dict:
                source_dict[rs][o] = {'file': output_dict[o],
                                      'type': rt}
            else:
                source_dict[rs] = {o: {'file': output_dict[o],
                                       'type': rt}}

        self.sd = source_dict

    def organize_files(self, target_dir):

        if not hasattr(self, 'sd'):
            self.build_source_dict()

        for rs in self.sd:
            fm = FileMunger(self, target_dir, rs)
            fm.go()


class FileMunger(object):

    def __init__(self, sample_curator, target_dir, result_source):

        self.lib = sample_curator.lib
        self.start = target_dir
        self.target = target_dir
        self.rs = result_source
        print " > Result source: %s" % self.rs

        self.sod = sample_curator.sd[result_source]
        self.prep_output_subdir()

    def prep_output_subdir(self):

        source_subdir_dict = {'fastqc': os.path.join(self.lib, 'qcR1'),
                              'picard_align': self.lib + '_qc',
                              'picard_markdups': self.lib + 'MarkDups',
                              'picard_rnaseq': self.lib + '_al',
                              'trinity': self.lib}

        if self.rs in source_subdir_dict:
            out_subdir = source_subdir_dict[self.rs]
        else:
            out_subdir = ''

        self.subdir = out_subdir

    def rename_files(self):

        source_output_dict = self.sod

        result_file_dict = {'trimmed_fastq': self.lib + '_trimmed.fastq',
                            'fastqc_qc_html': 'fastqc_report.html',
                            'fastqc_qc_txt': 'fastqc_data.txt',
                            'picard_align_metrics_html': 'Picard_Alignment_Summary_Metrics_html.html',
                            'picard_markdups_metrics_html': 'MarkDups_Dupes_Marked_html.html',
                            'trinity_fasta': 'Trinity.fasta',
                            'tophat_stats_metrics_txt': self.lib + 'ths.txt',
                            'picard_rnaseq_metrics_html': 'RNA_Seq_Metrics_html.html',
                            'htseq_counts_txt': self.lib + '_count.txt',
                            'tophat_alignments_bam': self.lib + '.bam',
                            'htseq_metrics_txt': self.lib + 'mm.txt',
                            'workflow_log_txt': self.lib + '_workflow_log.txt'}

        type_subdir_dict = {'qc': 'QC',
                            'metrics': 'metrics',
                            'counts': 'counts',
                            'alignments': 'alignments',
                            'trimmed': 'TrimmedFastqs',
                            'trinity': 'Trinity',
                            'log': 'logs'}

        dirs_to_bundle = []
        for idx,o in enumerate(source_output_dict):
            print ("   (file %d of %d)" %
                   (idx + 1, len(source_output_dict)))
            rf = source_output_dict[o]['file']
            rt = source_output_dict[o]['type']

            if self.rs is not 'fastq':
                out_dir = os.path.join(self.target, type_subdir_dict[rt], self.subdir)
                if not os.path.isdir(out_dir):
                    print "   - Creating directory %s" % out_dir
                    os.makedirs(out_dir)

                if len(self.subdir) and not self.rs == 'trinity':
                    dirs_to_bundle.append(out_dir)

                src_file = os.path.join(self.start, rt, os.path.basename(rf))
                target_file = os.path.join(out_dir, result_file_dict[o])
                if os.path.exists(target_file):
                    print "   - Target file %s already exists" % target_file
                elif not os.path.exists(src_file):
                    print "   - Source file %s not found" % src_file
                else:
                    print "   - Copying %s to %s" % (src_file, target_file)
                    shutil.move(src_file, target_file)
        self.bundle = list(set(dirs_to_bundle))

    def bundle_files(self):
        for d in self.bundle:
            print "   - Zipping up %s" % d
            shutil.make_archive(d, 'zip', d)
            shutil.rmtree(d)

    def go(self):
        self.rename_files()
        self.bundle_files()

def main(argv):
    flowcell_dir = sys.argv[1]
    CompileController(flowcell_dir).go()

if __name__ == "__main__":
   main(sys.argv[1:])
