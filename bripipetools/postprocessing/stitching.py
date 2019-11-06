"""
Combine parsed data from a set of batch processing output files and write to a
single CSV file.
"""
import logging
import os
import re
import csv

import pandas as pd

from .. import io
from .. import parsing
from .. import util

logger = logging.getLogger(__name__)


class OutputStitcher(object):
    """
    Given a path to an output folder or list of files, combine parsed data
    from files and write CSV.
    """
    def __init__(self, path, output_type=None, outputs=None):
        logger.debug("creating `OutputStitcher` for path '{}'".format(path))
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

    def _get_outputs(self, output_type):
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
                and not re.search('combined', f)
                and re.search(output_filetypes[output_type],
                              os.path.splitext(f)[-1])]

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
             'qc': {'fastqc': getattr(io, 'FastQCFile'),
                   'fastqc-R1': getattr(io, 'FastQCFile'),
                   'fastqc-R2': getattr(io, 'FastQCFile')},
            'counts': {'htseq': getattr(io, 'HtseqCountsFile')},
            'validation': {'sexcheck': getattr(io, 'SexcheckFile')}
        }
        logger.debug("matched parser '{}' for output type '{}' and source '{}'"
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
            logger.debug("parsing output file '{}'".format(o))
            out_items = parsing.parse_output_filename(o)
            proclib_id = out_items['sample_id']
            out_type = out_items['type']
            out_source = out_items['source']

            logger.debug("storing data from '{}' in '{}' '{}'".format(
                out_source, proclib_id, out_type))
            out_parser = self._get_parser(out_type, out_source)(path=o)

            self.data.setdefault(
                out_type, {}).setdefault(proclib_id, []).append(
                {out_source: out_parser.parse()}
            )

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
            for sample_id, sample_data in list(output_data.items()):
                header = [field for source in sample_data
                          for name, data in list(source.items())
                          for field in list(data.keys())]
                logger.debug("header row: {}".format(header))

                values = [value for source in sample_data
                          for name, data in list(source.items())
                          for value in list(data.values())]
                logger.debug("values: {}".format(values))

                if not len(table_data):
                    table_data.append(['libId'] + sorted(header))
                    logger.debug("added header row: {}".format(table_data[-1]))

                table_data.append(
                    [sample_id] + [v for h, v in sorted(zip(header, values))]
                )
                logger.debug("added values row: {}".format(table_data[-1]))
        return table_data

    def _add_mapped_reads_column(self, data):
        """
        Add mapped_reads_w_dups column to metrics table data.
        """
        try:
            for idx, row in enumerate(data[1:]):
                metrics = dict(list(zip(data[0], row)))
                # handle pct mapped reads calculation differently for PE reads
                if(metrics['category'] == 'unpaired'):
                    mapped_reads = (float(metrics['unpaired_reads_examined'])
                                    / float(metrics['fastq_total_reads']))
                else:
                    mapped_reads = ((float(metrics['unpaired_reads_examined'])
                                    + float(metrics['read_pairs_examined']))
                                    / float(metrics['fastq_total_reads']))
                data[idx + 1].append(mapped_reads)
            data[0].append('mapped_reads_w_dups')
        except KeyError:
            logger.warning("required fields missing; skipping calculation "
                        "of 'mapped_reads_w_dups")
        return data

    def _build_combined_filename(self):
        """
        Parse input path to create filename for combined CSV file.
        """
        path_parts = re.sub('.*Illumina/|.*ICAC/', '', self.path).split('/')
        logger.debug("building combined filename from path parts {}"
                     .format(path_parts))
        run_items = parsing.parse_flowcell_run_id(path_parts[0])
        project_label = parsing.get_project_label(path_parts[1])
        date = util.matchdefault('[0-9]{6}', path_parts[1])
        if project_label != '' and run_items['flowcell_id'] != '':
            filename_base = '{}_{}_{}'.format(project_label,
                                              run_items['flowcell_id'],
                                              date)
        else:
            filename_base = path_parts[0]
        return '{}_combined_{}.csv'.format(filename_base.rstrip('_'),
                                           self.type)

    def _build_overrepresented_seq_table(self):
        """
        Parse and combine overrepresented sequences tables from
        FastQC files.
        """
        outputs = self._get_outputs(self.type)
        overrep_seq_table = pd.DataFrame([])
        if self.type == 'qc':
            for o in outputs:
                logger.debug("parsing overrepresented sequences "
                             "from output file '{}'".format(o))
                out_items = parsing.parse_output_filename(o)
                proclib_id = out_items['sample_id']
                out_type = out_items['type']
                out_source = out_items['source']

                logger.debug("storing data from {} in {} {}".format(
                    out_source, proclib_id, out_type))
                out_parser = io.FastQCFile(path=o)
                o_table = (pd.DataFrame(out_parser
                                        .parse_overrepresented_seqs())
                           .assign(libId=proclib_id))
                logger.debug("found {} overrepresented sequence(s) "
                             "for sample '{}'".format(len(o_table), proclib_id))
                overrep_seq_table = overrep_seq_table.append(o_table)
        return overrep_seq_table

    def write_overrepresented_seq_table(self):
        """
        Write combined overrepresented sequences table to CSV file.
        """
        table_path = os.path.join(self.path,
                                  self._build_combined_filename())
        table_path = re.sub('_qc', '_overrep_seqs', table_path)
        table_data = self._build_overrepresented_seq_table()
        logger.debug("writing overrepresented seqs to file '{}'"
                     .format(table_path))
        table_data.to_csv(table_path, index=False)

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
                writer = csv.writer(f, lineterminator='\n')
                for row in table_data:
                    writer.writerow(row)
        return table_path
