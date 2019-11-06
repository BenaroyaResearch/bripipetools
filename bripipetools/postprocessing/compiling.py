"""
Compile combined/stitched 'summary' outputs of different types from
batch processing and write to a single CSV file.
"""
import logging
import os
import re
import csv

logger = logging.getLogger(__name__)


class OutputCompiler(object):
    """
    Reads combined output tables from list of file paths and compiles
    into single table, stored in a file at the project level.
    """
    def __init__(self, paths):
        logger.debug("creating `OutputCompiler` instance")
        self.paths = paths

    def _read_data(self):
        """
        Read, sort, and store data for each output file.
        """
        self.data = []

        for p in self.paths:
            logger.debug("parsing output file '{}'".format(p))
            with open(p) as f:
                p_data = list(csv.reader(f))
                self.data.append([p_data[0]] + sorted(p_data[1:]))

    def _build_table(self):
        """
        Combine data into table for writing; only keep sample IDs
        (first column of each file, with header 'libId') from first
        file in list.
        """
        table_data = self.data[0]
        for i in range(len(self.data))[1:]:
            table_data = [a + b[1:] for a, b in zip(table_data, self.data[i])]
        return table_data

    def _build_combined_filename(self):
        """
        Modify input path to create filename for combined CSV file.
        """
        return re.sub(r'(?<=combined_)\w*', 'summary-data',
                      os.path.basename(self.paths[0]))

    def write_table(self):
        """
        Write the combined table to a CSV file.
        """
        self._read_data()
        table_data = self._build_table()
        project_path = os.path.dirname(os.path.dirname(self.paths[0]))
        table_path = os.path.join(project_path,
                                  self._build_combined_filename())
        logger.debug("writing to file '{}'".format(table_path))
        with open(table_path, 'w') as f:
            writer = csv.writer(f, lineterminator='\n')
            for row in table_data:
                writer.writerow(row)
        return table_path
