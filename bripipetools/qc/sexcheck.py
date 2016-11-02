"""
Class and methods to perform routine sex check on all processed libraries.
"""
import logging
import os
import csv

import pandas as pd

from .. import parsing

logger = logging.getLogger(__name__)


class SexChecker(object):
    """
    Reads gene counts for a processed library, maps genes to X and Y
    chromosomes, computes ratio of Y to X counts, gives predicted sex
    based on pre-defined rule.
    """
    def __init__(self, processedlibrary, reference, workflowbatch_id,
                 genomics_root):
        logger.debug("creating an instance of SexChecker for processed"
                     " library '{}', workflow batch ID '{}', with "
                     "genomics root '{}'"
                     .format(processedlibrary._id,
                             workflowbatch_id,
                             genomics_root))
        self.processedlibrary = processedlibrary
        self.reference = reference
        self.workflowbatch_id = workflowbatch_id
        self.genomics_root = genomics_root
        self._compute_x_y_data()

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
        Count and store the number of Y and X genes detected, where
        detected = count > 0, as well as the total number of Y and X
        counts.
        """
        self._get_x_y_counts()
        self.data = {}
        self.data['x_genes'] = len(self.x_counts)
        self.data['y_genes'] = len(self.y_counts)
        self.data['x_counts'] = sum(self.x_counts['count'])
        self.data['y_counts'] = sum(self.y_counts['count'])
        self.data['total_counts'] = self.total_counts

    def _compute_y_x_gene_ratio(self):
        """
        Calculate the ratio of Y genes detected to X genes detected.
        """
        self.data['y_x_gene_ratio'] = (float(self.data['y_genes'])
                                       / float(self.data['x_genes']))

    def _compute_y_x_count_ratio(self):
        """
        Calculate the ratio of Y counts to X counts.
        """
        self.data['y_x_count_ratio'] = (float(self.data['y_counts'])
                                        / float(self.data['x_counts']))

    def _predict_sex(self):
        """
        Returns predicted sex based on X/Y gene equation and cutoff.
        """
        self._compute_y_x_gene_ratio()
        logger.debug("ratio of detected Y genes to detected X genes: {}"
                     .format(self.data['y_x_gene_ratio']))

        self._compute_y_x_count_ratio()
        logger.debug("ratio of Y counts to X counts: {}"
                     .format(self.data['y_x_count_ratio']))

        cutoff = 1
        equation = '(y_counts^2 / total_counts) > cutoff'
        value = (float(self.data['y_counts']**2)
                 / float(self.data['total_counts']))
        logger.debug("value for {} is {}"
                     .format(self.processedlibrary._id, value))
        self.data['sexcheck_eqn'] = equation
        self.data['sexcheck_cutoff'] = cutoff

        if value > cutoff:
            self.data['predicted_sex'] = 'male'
        else:
            self.data['predicted_sex'] = 'female'
        self.data['sex_check'] = None

    def _write_data(self, data):
        """
        Save the sex validation data to a new file.
        """
        counts_path = self._get_counts_path()
        project_path = os.path.dirname(os.path.dirname(counts_path))
        output_filename = '{}_{}_sexcheck_validation.csv'.format(
            parsing.get_library_id(counts_path),
            parsing.get_flowcell_id(counts_path))
        output_dir = os.path.join(project_path, 'validation')
        output_path = os.path.join(output_dir, output_filename)
        logger.debug("saving sex check file {} to {}"
                     .format(output_filename, output_dir))
        if not os.path.isdir(output_dir):
            logger.debug("creating directory {}".format(output_dir))
            os.makedirs(output_dir)
        with open(output_path, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)
        return output_path

    def update(self):
        """
        Add predicted sex validation field to processed library outputs and
        return processed library object.
        """
        if 'sex_check' not in self.data:
            logger.debug("predicting sex based on Y-to-X gene ratio")
            self._predict_sex()
        self._write_data(self.data)
        processed_data = [d for d in self.processedlibrary.processed_data
                          if d['workflowbatch_id']
                          == self.workflowbatch_id][0]
        processed_data.setdefault('validation', {})['sex_check'] = self.data
        return self.processedlibrary
