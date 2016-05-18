import os

class FilePacketManager(object):
    def __init__(self, packet_info, packet_key, target_dir):
        """
        Prepares instructions for munging operations such as renaming, moving,
        or bundling for a packet of annotated files.

        :type packet_info: dict
        :param packet_info: A dict representing a packet of files corresponding
            to a particular key (e.g., a sample); each files are grouped by
            ``source`` into separate dicts, with fields for file path and type
        :type packet_key: str
        :param packet_key: A string representing the key or label for the
            current packet of files.
        :type target_dir: str
        :param target_dir: Path to folder where final files are to be saved.
        """

        self.packet_info = packet_info
        self.packet_key = packet_key
        self.target_dir = target_dir

    def _get_type_subdir(self, file_type):
        """
        For each file in the file packet, create folders corresponding to type.
        """
        # packet_info = self.packet_info

        type_subdir_dict = {'qc': 'QC',
                            'metrics': 'metrics',
                            'counts': 'counts',
                            'alignments': 'alignments',
                            'trimmed': 'TrimmedFastqs',
                            'trinity': 'Trinity',
                            'log': 'logs'}

        # for file_names in packet_info.values():
        #     for f in file_names.values():
        #         type_subdir = type_subdir_dict.get(f['type'], '')
        #         f['target_dir'] = os.path.join(self.target_dir, type_subdir)

        return type_subdir_dict.get(file_type, '')

    def _get_bundle_subdir(self, source):
        """
        For each source in the file packet, create any subfolders needed
        for bundling/zipping multiple files.

        :rtype: dict
        :return: A modified version of the ``packet_info`` dict with target
            subdirectory stored in the ``subdir`` field for each source.
        """
        packet_key = self.packet_key
        # packet_info = self.packet_info

        source_subdir_dict = {'fastqc': os.path.join(packet_key, 'qcR1'),
                              'picard_align': '{}_qc'.format(packet_key),
                              'picard_markdups': '{}MarkDups'.format(packet_key),
                              'picard_rnaseq': '{}_al'.format(packet_key),
                              'trinity': packet_key}

        # for source in packet_info:
        #     packet_info[source]['subdir'] = source_subdir_dict.get(source, '')
        return source_subdir_dict.get(source, '')

    def _get_new_file_name(self, file_name):

        packet_key = self.packet_key

        file_name_dict = {'trimmed_fastq': '{}_trimmed.fastq'.format(packet_key),
                            'fastqc_qc_html': 'fastqc_report.html',
                            'fastqc_qc_txt': 'fastqc_data.txt',
                            'picard_align_metrics_html': 'Picard_Alignment_Summary_Metrics_html.html',
                            'picard_markdups_metrics_html': 'MarkDups_Dupes_Marked_html.html',
                            'trinity_fasta': 'Trinity.fasta',
                            'tophat_stats_metrics_txt': '{}ths.txt'.format(packet_key),
                            'picard_rnaseq_metrics_html': 'RNA_Seq_Metrics_html.html',
                            'htseq_counts_txt': '{}_count.txt'.format(packet_key),
                            'tophat_alignments_bam': '{}.bam'.format(packet_key),
                            'htseq_metrics_txt': '{}mm.txt'.format(packet_key),
                            'workflow_log_txt': '{}_workflow_log.txt'.format(packet_key)}

        return file_name_dict.get(file_name, '')

    def _build_munge_instructions(self, file_source, file_name, file_details):
        packet_key = self.packet_key
        packet_info = self.packet_info

        return os.path.join(self.target_dir,
                            self._get_type_subdir(file_details['type']),
                            self._get_bundle_subdir(file_source),
                            self._get_new_file_name(file_name))

    def munge_files(self):
        """
        Creates a file munging job for each ``source``, where files
        corresponding to that source will be renamed, moved, or bundled as
        necessary.
        """
        packet_info = self.packet_info
        for (source, source_files) in packet_info.items():
            print " > Result source: %s" % source
            for (file_name, file_details) in source_files.items():
                # print ("   (file %d of %d)" %
                #        (idx + 1, len(source_output_dict)))
                new_file = self._build_munge_instructions(source, file_name,
                                                          file_details)
                print(file_details['file'], new_file)
            # munger = fileops.FileMunger(source_files, source)


class FileMunger(object):
    def __init__(self, file_info, file_key):
        """
        Performs operations such as renaming, moving, or bundling (zipping) on
        an annotated set of files.

        :type file_info: dict
        :param file_info: A dict representing a packet of files corresponding
            to a particular key (e.g., a source) with fields for file path,
            type, and subfolder.
        :type file_key: str
        :param file_key: A string representing the key or label for the
            set of files.
        """
        self.file_info = file_info
        self.file_key = file_key
        # self.rs = result_source
        #
        # self.sod = sample_curator.sd[result_source]
        # self.prep_output_subdir()

    def rename_files(self):
        """
        For each file in the ``file_info``
        """
        source_output_dict = self.sod





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
