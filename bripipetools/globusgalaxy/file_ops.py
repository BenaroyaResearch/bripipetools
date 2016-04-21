
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
