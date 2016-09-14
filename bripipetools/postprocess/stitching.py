"""
Combine parsed data from a set of batch processing output files and write to a
single CSV file.
"""
import logging
logger = logging.getLogger(__name__)
import os
import re
import csv

import pandas as pd

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
                   'counts': {'htseq': getattr(io, 'HtseqCountsFile')}}
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
                out_type, {}).setdefault(proclib_id, []).append(
                {out_source: out_parser.parse()})

    def _build_table(self):
        """
        Combine parsed data into table for writing.
        """
        output_data = self.data[self.type]
        if self.type == 'counts':
            logger.info("combining counts data")
            for idx, (sample_id, sample_data) in enumerate(output_data.items()):
                data = sample_data[0]['htseq']
                data = data.rename(index=str, columns={'count': sample_id})
                if idx == 0:
                    table_data = data
                else:
                    table_data = pd.merge(table_data, data, on='geneName')
        else:
            logger.info("combining non-counts data")
            table_data = []
            for sample_id, sample_data in output_data.items():
                header = [field for source in sample_data
                          for name, data in source.items()
                          for field in data.keys()]
                logger.debug("header row: {}".format(header))

                values = [value for source in sample_data
                          for name, data in source.items()
                          for value in data.values()]
                logger.debug("values: {}".format(values))

                if not len(table_data):
                    table_data.append(['libId'] + sorted(header))
                    logger.debug("added header row: {}".format(table_data[-1]))

                table_data.append([sample_id] + [v for h, v
                                                 in sorted(zip(header,
                                                               values))])
                logger.debug("added values row: {}".format(table_data[-1]))
        return table_data

    def _add_mapped_reads_column(self, data):
        """
        Add mapped_reads_w_dups column to table data.
        """
        for idx, row in enumerate(data[1:]):
            metrics = dict(zip(data[0], row))
            mapped_reads = (float(metrics['UNPAIRED_READS_EXAMINED'])
                            / float(metrics['fastq_total_reads']))
            data[idx + 1].append(mapped_reads)
        data[0].append('mapped_reads_w_dups')
        return data

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
        table_data = self._build_table()
        if self.type == 'metrics':
            table_data = self._add_mapped_reads_column(table_data)
        table_path = os.path.join(self.path,
                                  self._build_combined_filename())
        logger.debug("writing to file {}".format(table_path))
        if self.type == 'counts':
            table_data.to_csv(table_path, index=False)
        else:
            with open(table_path, 'w') as f:
                writer = csv.writer(f)
                for row in table_data:
                    writer.writerow(row)
