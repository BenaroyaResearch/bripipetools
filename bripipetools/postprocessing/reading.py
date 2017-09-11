"""
Read a single output file and return.
"""
import logging
import os
import re
import csv
import string

import pandas as pd

from .. import io
from .. import parsing
from .. import util

logger = logging.getLogger(__name__)


class OutputReader(object):
    """
    Given a path to an output folder or list of files, combine parsed data
    from files and write CSV.
    """
    def __init__(self, path, output_type=None):
        logger.debug("creating `OutputReader` for path '{}'".format(path))
        self.path = path
        if output_type is None:
            self.type = self._sniff_output_type()

    def _sniff_output_type(self):
        """
        Return predicted output type based on specified path.
        """
        output_types = ['metrics', 'QC', 'counts', 'validation']
        output_match = [t.lower() for t in output_types
                        if re.search(t, self.path)]
        if len(output_match):
            return output_match[0]

    def _get_outputs(self, library, output_type):
        """
        Return list of outputs of specified type.
        """
        output_filetypes = {'metrics': 'txt|html',
                            'qc': 'txt',
                            'counts': 'txt',
                            'validation': 'csv'}
        return [os.path.join(self.path, f)
                for f in os.listdir(self.path)
                if re.search(output_type, f)
                and re.search(library, f)
                and not re.search('combined', f)
                and re.search(output_filetypes[output_type], os.path.splitext(f)[-1])]

    def _get_parser(self, output_type, output_source):
        """
        Return the appropriate parser for the current output file.
        """
        parsers = {
            'metrics': {'htseq': getattr(io, 'HtseqMetricsFile'),
                        'picard-rnaseq': getattr(io, 'PicardMetricsFile'),
                        'picard-markdups': getattr(io, 'PicardMetricsFile'),
                        'picard-align': getattr(io, 'PicardMetricsFile'),
                        'picard-alignment': getattr(io, 'PicardMetricsFile'),
                        'tophat-stats': getattr(io, 'TophatStatsFile')},
            'qc': {'fastqc': getattr(io, 'FastQCFile')},
            'counts': {'htseq': getattr(io, 'HtseqCountsFile')},
            'validation': {'sexcheck': getattr(io, 'SexcheckFile')}
        }
        logger.debug("matched parser '{}' for output type '{}' and source '{}'"
                     .format(parsers[output_type][output_source],
                             output_type, output_source))
        return parsers[output_type][output_source]

    def read_data(self, seqlib_id):
        """
        Parse and store data for a output file.
        """
        outputs = self._get_outputs(seqlib_id, self.type)

        self.data = {}

        for o in outputs:
            logger.debug("parsing output file '{}'".format(o))
            out_items = parsing.parse_output_filename(o)
            proclib_id = out_items['sample_id']
            out_type = out_items['type']
            out_source = out_items['source']

            logger.debug("storing data from '{}' in '{}' '{}'".format(out_source, proclib_id, out_type))
            out_parser = self._get_parser(out_type, out_source)(path=o)

            #self.data.setdefault(out_type, {}).setdefault(proclib_id, []).append({out_source: out_parser.parse()})
            dataframe = out_parser.parse()
            #logger.info("dataframe: {}".format(dataframe))
            if self.type == 'counts':
                self.data = dataframe.set_index('geneName')['count'].to_dict()
            else:
                mod_source = out_source.replace("-", "_")
                self.data.setdefault(out_type, []).append({mod_source: out_parser.parse()})
        
        return self.data
        
        
        
