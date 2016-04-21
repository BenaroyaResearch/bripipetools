class GlobusOutputAnnotator(object):
    def __init__(self, sample_output_map, sample):
        """
        Methods for annotating / classifying output files for a selected sample.

        :type sample_output_map: dict
        :param sample_output_map: Dict mapping samples to expected output
            files in the flowcell folder.

        :type sample: str
        :param sample: Name of current sample (i.e., a key in the
            sample-to-output mapping dictionary)
        """
        self.output_map = sample_output_map[sample]
        self.sample = sample

    def get_output_type(self, output_name):
        """
        Return the type of a selected output.

        :type output_name: str
        :param output_name: Parameter name of the current output file (e.g.,
            'tophat_alignments_bam_out')

        :rtype: str
        :return: A string indicating the filetype (extension) of the output
            file (e.g., 'bam').
        """
        output_name = re.sub('_[a-z]+$', '', output_name)
        return strings.matchdefault('(?<=_)[a-z]+$', output_name, output_name)

    def get_output_source(self, output_name):
        """
        Return the source of or tool used to generate the current output file.

        :type output_name: str
        :param output_name: Parameter name of the current output file (e.g.,
            'tophat_alignments_bam_out')

        :rtype: str
        :return: A string indicating the source of the output file (e.g.,
            'tophat').
        """
        # TODO: replace with separate parameter configs (json or yaml)
        if not re.search('fastq$', output_name):
            output_sources = ['picard_align', 'picard_markdups', 'picard_rnaseq',
                              'htseq', 'trinity', 'tophat', 'tophat_stats',
                              'fastqc', 'workflow_log']
            return [s for s in output_sources
                    if re.search(s.lower(), output_name)][0]
        else:
            output_sources = ['fastq', 'trimmed_fastq']
            return [s for s in output_sources
                    if re.search('^' + s.lower() + '$', output_name)][0]

    def get_output_info(self):
        """
        For the current sample, group output files by source; return the path
        and type of each file.

        :rtype: dict
        :return: A dict, where for each ``source`` key, a list of dicts is
            stored, containing the ``file`` (path) and ``type`` of each
            corresponding output file.
        """
        source_output_map = {}
        for o in self.output_map:
            output_type = self.get_output_type(o)
            output_source = self.get_output_source(o)

            source_ouput_map.setdefault(output_source, {})[o] =
                {'file': output_dict[o], 'type': output_type}

            # if rs in source_dict:
            #     source_output_map[rs][o] = {'file': output_dict[o],
            #                           'type': rt}
            # else:
            #     source_dict[rs] = {o: {'file': output_dict[o],
            #                            'type': rt}}

        return source_output_map
