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
        Based on pre-defined translations in lookup table, return the folder
        name corresponding to type of result.

        :type file_type: str
        :param file_type: File type used in lookup table.

        :rtype: str
        :return: Formatted folder name corresponding to result type.
        """
        type_subdir_dict = {'qc': 'QC',
                            'metrics': 'metrics',
                            'counts': 'counts',
                            'alignments': 'alignments',
                            'trimmed': 'TrimmedFastqs',
                            'trinity': 'Trinity',
                            'log': 'logs'}

        return type_subdir_dict.get(file_type, '')

    def _get_bundle_subdir(self, file_source):
        """
        Based on pre-defined translations in lookup table, return the path of
        the subfolder for files from a specified source that need to be bundled
        (compressed) in a subsequent step. The ``packet_key`` is also inserted
        as needed.

        :type file_source: str
        :param file_source: File source used in lookup table.

        :rtype: str
        :return: Formatted sub-folder name corresponding to file source; if
            non-empty, sub-folder should be bundled after all individual files
            from the source have been moved/renamed.
        """
        packet_key = self.packet_key

        source_subdir_dict = {'fastqc': os.path.join(packet_key, 'qcR1'),
                              'picard_align': '{}_qc'.format(packet_key),
                              'picard_markdups': '{}MarkDups'.format(packet_key),
                              'picard_rnaseq': '{}_al'.format(packet_key),
                              'trinity': packet_key}

        return source_subdir_dict.get(file_source, '')

    def _get_new_file_name(self, file_id):
        """
        Based on pre-defined translations in lookup table, return the final
        file name corresponding to a file identifier. The ``packet_key`` is
        also inserted into the new file name as instructed by string values
        in the lookup table.

        :type file_id: str
        :param file_id: File identifier used in lookup table; for Globus
            Galaxy batch submissions, this corresponds to a parameter name
            for an output file (e.g., 'tophat_alignments_bam').

        :rtype: str
        :return: A string representing the new file name (i.e., basename) for
            the current file; or, an empty string, if file ID not found in
            lookup table.
        """
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

        return file_name_dict.get(file_id, '')

    def _build_new_file_path(self, file_source, file_id, file_details):
        """
        Return the final path for file which is scheduled to be moved or
        renamed.
        """
        packet_key = self.packet_key
        packet_info = self.packet_info

        return os.path.join(self.target_dir,
                            self._get_type_subdir(file_details['type']),
                            self._get_bundle_subdir(file_source),
                            self._get_new_file_name(file_id))

    def munge_files(self):
        """
        Creates a file munging job for each ``source``, where files
        corresponding to that source will be renamed, moved, or bundled as
        necessary.
        """
        packet_info = self.packet_info
        for (source, source_files) in packet_info.items():
            print " > Result source: %s" % source
            for (file_id, file_details) in source_files.items():
                # print ("   (file %d of %d)" %
                #        (idx + 1, len(source_output_dict)))
                new_file = self._build_new_file_path(source, file_id,
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
