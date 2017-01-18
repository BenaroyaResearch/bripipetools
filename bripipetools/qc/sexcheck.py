"""
Class and methods to perform routine sex check on all processed libraries.
"""
import logging
import os
import csv

import pandas as pd

from .. import parsing
from . import SexPredictor, SexVerifier

logger = logging.getLogger(__name__)


class SexChecker(object):
    """
    Reads gene counts for a processed library, maps genes to X and Y
    chromosomes, computes ratio of Y to X counts, gives predicted sex
    based on pre-defined rule.
    """
    def __init__(self, processedlibrary, reference, workflowbatch_id,
                 genomics_root, db):
        logger.debug("creating an instance of `SexChecker` for processed "
                     "library '{}', workflow batch ID '{}', with "
                     "genomics root '{}'"
                     .format(processedlibrary._id,
                             workflowbatch_id,
                             genomics_root))
        self.processedlibrary = processedlibrary
        self.reference = reference
        self.workflowbatch_id = workflowbatch_id
        self.genomics_root = genomics_root
        self.db = db

    def _load_x_genes(self, ref='grch38'):
        """
        Read X chromosome gene IDs from file and return data frame.
        """
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'data'
        )
        x_genes_file = os.path.join(data_path, '{}_gene_ids_x.csv'.format(ref))

        return pd.read_table(x_genes_file, names=['geneName'], skiprows=1)

    def _load_y_genes(self, ref='grch38'):
        """
        Read Y chromosome gene IDs from file and return data frame.
        """
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'data'
        )
        y_genes_file = os.path.join(data_path, '{}_gene_ids_y.csv'.format(ref))

        return pd.read_table(y_genes_file, names=['geneName'], skiprows=1)

    def _get_counts_path(self):
        """
        Construct the absolute path to the counts file for the specified
        workflow batch.
        """
        return [os.path.join(self.genomics_root,
                             d['outputs']['counts'][0]['file'].lstrip('/'))
                for d in self.processedlibrary.processed_data
                if d['workflowbatch_id'] == self.workflowbatch_id][0]

    def _get_x_y_counts(self):
        """
        Extract and store counts for X and Y genes; also store count total.
        """
        counts_df = pd.read_table(self._get_counts_path(),
                                  names=['geneName', 'count'])
        logger.debug("counts data frame has {} rows".format(len(counts_df)))
        self.total_counts = sum(counts_df[counts_df['count'] > 0]['count'])

        y_counts = pd.merge(self._load_y_genes(ref=self.reference), counts_df,
                            how='inner')
        self.y_counts = y_counts[y_counts['count'] > 0]
        logger.debug("detected {} Y gene(s)".format(len(self.y_counts)))
        x_counts = pd.merge(self._load_x_genes(ref=self.reference), counts_df,
                            how='inner')
        self.x_counts = x_counts[x_counts['count'] > 0]
        logger.debug("detected {} X gene(s)".format(len(self.x_counts)))

    def _compute_x_y_data(self):
        """
        Collect and store X and Y gene/count data as well as total counts
        for the current processed library.
        """
        self._get_x_y_counts()
        self.data = {
            'x_genes': len(self.x_counts),
            'y_genes': len(self.y_counts),
            'x_counts': sum(self.x_counts['count']),
            'y_counts': sum(self.y_counts['count']),
            'total_counts': self.total_counts,
        }

    def _predict_sex(self):
        """
        Return predicted sex based on X/Y gene equation and cutoff.
        """
        logger.debug("adding sex check QC info for '{}'"
                     .format(self.processedlibrary._id))
        self.data = SexPredictor(self.data).predict()

    def _verify_sex(self):
        """
        Compare predicted sex to reported sex.
        """
        logger.debug("verifying sex prediction")
        self.data = SexVerifier(
            data=self.data,
            processedlibrary=self.processedlibrary,
            db=self.db
        ).verify()

    def _write_data(self):
        """
        Save the sex validation data to a new file.
        """
        counts_path = self._get_counts_path()
        project_path = os.path.dirname(os.path.dirname(counts_path))
        output_filename = '{}_{}_sexcheck_validation.csv'.format(
            parsing.get_library_id(counts_path),
            parsing.get_flowcell_id(counts_path)
        )
        output_dir = os.path.join(project_path, 'validation')
        output_path = os.path.join(output_dir, output_filename)
        logger.debug("saving sex check file '{}' to '{}'"
                     .format(output_filename, output_dir))
        if not os.path.isdir(output_dir):
            logger.debug("creating directory '{}'".format(output_dir))
            os.makedirs(output_dir)
        with open(output_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=self.data.keys())
            writer.writeheader()
            writer.writerow(self.data)
        return output_path

    def update(self):
        """
        Add predicted sex validation field to processed library outputs and
        return processed library object.
        """
        if self.reference != 'grch38':
            return self.processedlibrary

        processed_data = [d for d in self.processedlibrary.processed_data
                          if d['workflowbatch_id']
                          == self.workflowbatch_id][0]
        logger.debug("predicting sex based on X and Y gene data")
        self._compute_x_y_data()
        self._predict_sex()
        self._verify_sex()
        self._write_data()

        processed_data.setdefault('validation', {})['sex_check'] = self.data
        return self.processedlibrary
