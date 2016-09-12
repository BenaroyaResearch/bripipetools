"""
Combine parsed data from a set of batch processing output files and write to a
single CSV file.
"""
import logging
logger = logging.getLogger(__name__)
import os
import re

from .. import io

class OutputStitcher(object):
    """
    Given a path to an output folder or list of files, combine parsed data
    from files and write CSV.
    """
    def __init__(self, path, output_type=None, outputs=None):

        self.path = path
        if output_type is None:
            self.type = self._sniff_output_type()

    def _sniff_output_type(self):
        """
        Return predicted output type based on specified path.
        """
        output_types = ['metrics', 'counts']
        return [t for t in output_types if re.search(t, self.path)][0]

    def _get_outputs(self, output_type):
        """
        Return list of outputs of specified type.
        """
        return [os.path.join(self.path, f)
                for f in os.listdir(self.path)
                if re.search(output_type, f)]

    def _parse_output_filename(self, output_filename):
        """
        Parse output name indicated by parameter tag in output file
        return individual components indicating processed library ID,
        output source, and type.
        """
        output_filename = os.path.basename(output_filename)
        output_name = os.path.splitext(output_filename)[0]
        name_parts = name.split('_')
        output_type = name_parts.pop(-1)
        source = name_parts.pop(-1)
        proclib_id = ('_').join(name_parts)

        return {'proclib_id': proclib_id, 'type': output_type,
                'source': source}

    def _get_parser(self, output_type, output_source):
        """
        Return the appropriate parser for the current output file.
        """
        parsers = {'metrics': {'htseq': getattr(io, 'HtseqMetricsFile'),
                               'picard_rnaseq': getattr(io, 'PicardMetricsFile'),
                               'picard_markdups': getattr(io, 'PicardMetricsFile'),
                               'picard_align': getattr(io, 'PicardMetricsFile')},
                   'counts': {'htseq': getattr(io, 'PicardMetricsFile')}}
        logger.debug("matched parser {} for output type {} and source {}"
                     .format(parsers[output_type][output_source],
                             output_type, output_source))
        return parsers[output_type][output_source]

    # def _read_data(self):
    #     """
    #     Parse and store data for each output file.
    #     """
    #     outputs = self._get_outputs(self.type)
    #     self.data = []
    #
    #     for o in outputs:
