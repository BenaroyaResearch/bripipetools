import os

from bripipetools.util import files

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
        type_subdir_dict = {'fastq': 'InputFastqs',
                            'qc': 'QC',
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

        file_name_dict = {'fastq': '{}_R1-final.fastq.gz'.format(packet_key),
                          'trimmed_fastq': '{}_trimmed.fastq'.format(packet_key),
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

    def munge_files(self, dry_run=False):
        """
        Creates a file munging job for each ``source``, where files
        corresponding to that source will be renamed, moved, or bundled as
        necessary.

        :type param: bool
        :param dry_run: If flag is ``True``, only print what would be done.
        """
        packet_info = self.packet_info
        for (source, source_files) in packet_info.items():
            print " > Result source: %s" % source
            for (file_id, file_details) in source_files.items():
                file_details['new_path'] = (self._build_new_file_path(
                                                source, file_id, file_details))

            munger = FileMunger(source_files, source, dry_run)
            munger.rename_files()

            # check whether to bundle files
            bundle_subdir = self._get_bundle_subdir(source)
            if len(bundle_subdir) and bundle_subdir != 'trinity':
                munger.bundle_files()

        # TODO: return something...


class FileMunger(object):
    def __init__(self, file_info, file_key, dry_run=False):
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
        :type param: bool
        :param dry_run: If flag is ``True``, only print what would be done.
        """
        self.file_info = file_info
        self.file_key = file_key
        self.dry_run = dry_run

    def _prep_output_dirs(self):
        """
        Check all files in ``file_info`` and create any folders in new paths
        that don't already exist.
        """
        file_info = self.file_info
        file_key = self.file_key

        for file_id, file_details in file_info.items():
            out_dir = os.path.dirname(file_details['new_path'])
            if not os.path.isdir(out_dir):
                print("   - Creating directory {}".format(out_dir))
                if not self.dry_run:
                    os.makedirs(out_dir)

    def rename_files(self):
        """
        For each file in the ``file_info``, rename/move to new path.
        """
        file_info = self.file_info
        file_key = self.file_key

        self._prep_output_dirs()

        rename_status = {}
        for idx, (file_id, file_details) in enumerate(file_info.items()):
            print("   (file {} of {})".format(idx + 1, len(file_info)))
            rename_status[file_id] = (files.SystemFile(file_details['path'])
                                      .rename(file_details['new_path'],
                                              self.dry_run))

        # TODO: improve error handling here...
        if len([fid for fid, status in rename_status.items()
                if status]):
            return 1
        else:
            return 0

    def bundle_files(self):
        """
        Create a zip archive for the folder where files in ``file_info`` have
        been moved; remove original folder.
        """
        file_info = self.file_info

        bundle_dir = os.path.dirname(file_info.values()[0]['new_path'])
        print("   - Zipping up {}".format(bundle_dir))
        if not self.dry_run:
            shutil.make_archive(bundle_dir, 'zip', bundle_dir)
            shutil.rmtree(bundle_dir)

        # TODO: return something...
