class GlobusOutputAnnotator(object):
    # TODO: this might make sense as a separate module for annotating outputs,
    # might overlap with similar tasks for Galaxy Datasets
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

    def _get_output_type(self, output):
        output_str = re.sub('_[a-z]+$', '', output)
        return strings.matchdefault('(?<=_)[a-z]+$', output_str,
                                    output_str)


    def _get_output_source(self, output):
        if not re.search('fastq$', output):
            output_sources = ['picard_align', 'picard_markdups', 'picard_rnaseq',
                              'htseq', 'trinity', 'tophat', 'tophat_stats', 'fastqc',
                              'workflow_log']
            return [s for s in output_sources
                    if re.search(s.lower(), output)][0]
        else:
            output_sources = ['fastq', 'trimmed_fastq']
            return [s for s in output_sources
                    if re.search('^' + s.lower() + '$', output)][0]

    def get_source_outputs(self):
        source_output_map = {}
        for o in self.output_map:
            rt = self._get_output_type(o)
            rs = self._get_output_source(o)

            source_ouput_map.setdefault(rs, {})[o] = {'file': output_dict[o],
                                                      'type': rt}

            # if rs in source_dict:
            #     source_output_map[rs][o] = {'file': output_dict[o],
            #                           'type': rt}
            # else:
            #     source_dict[rs] = {o: {'file': output_dict[o],
            #                            'type': rt}}

        self.source_outputs = source_output_map
