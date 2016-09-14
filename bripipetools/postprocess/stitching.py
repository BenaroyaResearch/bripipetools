"""
Combine parsed data from a set of batch processing output files and write to a
single CSV file.
"""
import logging
logger = logging.getLogger(__name__)
import os
import re
import csv

from .. import io
from .. import parsing
from .. import util

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
                if re.search(output_type, f)
                and not re.search('combined', f)]

    def _parse_output_filename(self, output_filename):
        """
        Parse output name indicated by parameter tag in output file
        return individual components indicating processed library ID,
        output source, and type.
        """
        output_filename = os.path.basename(output_filename)
        output_name = os.path.splitext(output_filename)[0]
        name_parts = output_name.split('_')
        output_type = name_parts.pop(-1)
        source = name_parts.pop(-1)
        if len(name_parts) <= 2:
            proclib_id = ('_').join(name_parts)
        else:
            source = ('_').join([name_parts.pop(-1), source])
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
                               'picard_align': getattr(io, 'PicardMetricsFile'),
                               'tophat_stats': getattr(io, 'TophatStatsFile')},
                   'counts': {'htseq': getattr(io, 'PicardMetricsFile')}}
        logger.debug("matched parser {} for output type {} and source {}"
                     .format(parsers[output_type][output_source],
                             output_type, output_source))
        return parsers[output_type][output_source]

    def _read_data(self):
        """
        Parse and store data for each output file.
        """
        outputs = self._get_outputs(self.type)
        self.data = {}

        for o in outputs:
            logger.debug("parsing output file {}".format(o))
            out_items = self._parse_output_filename(o)
            out_source, out_type, proclib_id = out_items.values()
            logger.debug("storing data from {} in {} {}".format(
                out_source, proclib_id, out_type))
            out_parser = self._get_parser(out_type, out_source)(path=o)

            self.data.setdefault(
                out_type, {proclib_id: []})[proclib_id].append(
                    {out_source: out_parser.parse()})

    def _build_table(self):
        """
        Combine parsed data into rows of a table for writing.
        """
        table_rows = []
        for sample_id, sample_data in self.data[self.type].items():
            if not len(table_rows):
                table_rows.append(['libId'] + [field
                                   for source in sample_data
                                   for name, data in source.items()
                                   for field in data.keys()])
                logger.debug("added header row: {}".format(table_rows[-1]))
            table_rows.append([sample_id] + [value
                               for source in sample_data
                               for name, data in source.items()
                               for value in data.values()])
            logger.debug("added values row: {}".format(table_rows[-1]))
        return table_rows

    def _build_combined_filename(self):
        """
        Parse input path to create filename for combined CSV file.
        """
        path_parts = re.sub('.*Illumina/', '', self.path).split('/')
        logger.debug("building combined filename from path parts {}"
                     .format(path_parts))
        run_items = parsing.parse_flowcell_run_id(path_parts[0])
        project_label = parsing.get_project_label(path_parts[1])
        date = util.matchdefault('[0-9]{6}', path_parts[1])
        filename_base = '{}_{}_{}'.format(project_label,
                                          run_items['flowcell_id'],
                                          date)
        return '{}_combined_{}.csv'.format(filename_base.rstrip('_'),
                                           self.type)

    def write_table(self):
        """
        Write the combined table to a CSV file.
        """
        self._read_data()
        table_rows = self._build_table()
        table_path = os.path.join(self.path,
                                  self._build_combined_filename())
        logger.debug("writing to file {}".format(table_path))
        with open(table_path, 'w') as f:
            writer = csv.writer(f)
            for row in table_rows:
                writer.writerow(row)
