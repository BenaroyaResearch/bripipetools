"""
Class and methods to perform routine sex check on all processed libraries.
"""
import logging
logger = logging.getLogger(__name__)
import os

import pandas as pd

from .. import io

class SexChecker(object):
    """
    Reads gene counts for a processed library, maps genes to X and Y
    chromosomes, computes ratio of Y to X reads, gives predicted sex
    based on pre-defined rule.
    """
    def __init__(self, processedlibrary, workflowbatch_id, genomics_root):
        logger.info("creating an instance of SexChecker for processed"
                    " library '{}', workflow batch ID '{}', with "
                    "genomics root '{}'"
                    .format(processedlibrary._id,
                            workflowbatch_id,
                            genomics_root))
        self.processedlibrary = processedlibrary
        self.workflowbatch_id = workflowbatch_id
        self.genomics_root = genomics_root

    def _load_x_genes(self, ref='grch38'):
        """
        Read X chromosome gene IDs from file and return data frame.
        """
        x_genes_file = './data/{}_gene_ids_x.csv'.format(ref)
        return pd.read_table(x_genes_file, names=['geneName'], skiprows=1)

    def _load_y_genes(self, ref='grch38'):
        """
        Read Y chromosome gene IDs from file and return data frame.
        """
        y_genes_file = './data/{}_gene_ids_y.csv'.format(ref)
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

    def _compute_y_x_ratio(self):
        """
        Return the ratio of Y genes detected to X genes detected, where
        detected = count > 0.
        """
        counts_df = pd.read_table(self._get_counts_path(),
                                  names=['geneName', 'count'])
        logger.debug("counts data frame has {} rows".format(len(counts_df)))
        total_y = sum(pd.merge(self._load_y_genes(), counts_df,
                               how='inner')['count'] > 0)
        logger.debug("detected {} Y genes".format(total_y))
        total_x = sum(pd.merge(self._load_x_genes(), counts_df,
                               how='inner')['count'] > 0)
        logger.debug("detected {} X genes".format(total_x))
        return float(total_y) / float(total_x)

    def _predict_sex(self, x_y_ratio):
        """
        Returns predicted sex based on ratio of detected Y to X genes.
        """
        return 'male' if x_y_ratio > 0.1 else 'female'

    def update(self):
        """
        Add predicted sex validation field to processed library outputs and
        return processed library object.
        """
        y_x_ratio = self._compute_y_x_ratio()
        processed_data = [d for d in self.processedlibrary.processed_data
                          if d['workflowbatch_id'] == self.workflowbatch_id][0]
        processed_data.setdefault('validations', {})['sex_check'] = {
            'y_x_ratio': y_x_ratio,
            'predicted_sex': self._predict_sex(y_x_ratio),
            'pass': None
        }
        logger.info("{}".format(processed_data))
        return self.processedlibrary
