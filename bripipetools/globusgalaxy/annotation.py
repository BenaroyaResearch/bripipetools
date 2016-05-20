"""
Classify / provide details for output files.
"""

import re

from bripipetools.util import strings

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

    def get_output_type(self, output_id):
        """
        Return the type of a selected output.

        :type output_id: str
        :param output_id: Parameter name of the current output file (e.g.,
            'tophat_alignments_bam')

        :rtype: str
        :return: A string indicating the result type of the output file (e.g.,
            'alignments' for 'tophat_alignments_bam').
        """
        # trim trailing characters following last '_'
        output_id = re.sub('_[a-z]+$', '', output_id)

        # match characters following last remaining '_' or return whole string
        return strings.matchdefault('(?<=_)[a-z]+$', output_id, output_id)

    def get_output_source(self, output_id):
        """
        Return the source of or tool used to generate the current output file.

        :type output_id: str
        :param output_id: Parameter name of the current output file (e.g.,
            'tophat_alignments_bam')

        :rtype: str
        :return: A string indicating the source of the output file (e.g.,
            'tophat').
        """
        # TODO: replace with separate parameter configs (json or yaml)
        if not re.search('fastq$', output_id):
            output_sources = ['picard_align', 'picard_markdups', 'picard_rnaseq',
                              'htseq', 'trinity', 'tophat', 'tophat_stats',
                              'fastqc', 'workflow_log']
            return [s for s in output_sources
                    if re.search(s.lower(), output_id)][0]
        else:
            output_sources = ['fastq', 'trimmed_fastq']
            return [s for s in output_sources
                    if re.search('^' + s.lower() + '$', output_id)][0]

    def get_output_info(self):
        """
        For the current sample, group output files by source; return the path
        and type of each file.

        :rtype: dict
        :return: A dict, where for each ``source`` key, a list of dicts is
            stored, containing the ``path`` and ``type`` of each
            corresponding output file.
        """
        source_output_map = {}
        for output_id in self.output_map:
            output_type = self.get_output_type(output_id)
            output_source = self.get_output_source(output_id)

            source_output_map.setdefault(output_source, {})[output_id] = \
                {'path': self.output_map[output_id], 'type': output_type}

        return source_output_map
