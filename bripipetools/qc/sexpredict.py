"""
Class and methods to perform routine sex check on all processed libraries.
"""
import logging

logger = logging.getLogger(__name__)


class SexPredictor(object):
    """
    Predicts sex based X and Y gene count data using a pre-defined rule.
    """
    def __init__(self, data, qc_opts):
        logger.debug("creating `SexPredictor` instance")
        self.data = data
        self.sexmodel = qc_opts["sexmodel"]
        self.sexcutoff = qc_opts["sexcutoff"]

    def _compute_y_x_gene_ratio(self):
        """
        Calculate the ratio of Y genes detected to X genes detected,
        where detected = count > 0.
        """
        n_y = float(self.data['y_genes'])
        n_x = float(self.data['x_genes'])
        if n_x == 0:
            # for now, set ot number of y counts.
            # This nicely handles instance where
            # n_y = n_x = 0, but may need to be revisited
            self.data['y_x_gene_ratio'] = n_y
        else:
            self.data['y_x_gene_ratio'] = n_y / n_x

    def _compute_y_x_count_ratio(self):
        """
        Calculate the ratio of Y counts to X counts.
        """
        n_y = float(self.data['y_counts'])
        n_x = float(self.data['x_counts'])
        if n_x == 0:
            self.data['y_x_count_ratio'] = n_y
        else:
            self.data['y_x_count_ratio'] = n_y / n_x

    def _predict_sex(self):
        """
        Return predicted sex based on X/Y gene equation and cutoff.
        """
        self._compute_y_x_gene_ratio()
        logger.debug("ratio of detected Y genes to detected X genes: {}"
                     .format(self.data['y_x_gene_ratio']))

        self._compute_y_x_count_ratio()
        logger.debug("ratio of Y counts to X counts: {}"
                     .format(self.data['y_x_count_ratio']))

        possible_eqs={
            'y_sq_over_tot': '(y_counts^2 / total_counts) > cutoff',
            'gene_ratio': '(y_genes / x_genes) > cutoff',
            'counts_ratio': '(y_counts / x_counts) > cutoff'
        }
        equation = possible_eqs[self.sexmodel]
        logger.debug("using equation: {}".format(equation))

        if self.sexmodel == 'y_sq_over_tot':
            n_y_sq = float(self.data['y_counts'])**2
            n_tot = float(self.data['total_counts'])
            if n_tot == 0:
                value = n_y_sq
            else:
                value = n_y_sq / n_tot

        elif self.sexmodel == 'gene_ratio':
            value = float(self.data['y_x_gene_ratio'])

        elif self.sexmodel == 'counts_ratio':
            value = float(self.data['y_x_count_ratio'])

        logger.debug("value for current sample is {}"
                     .format(value))
        self.data['sexcheck_eqn'] = equation
        self.data['sexcheck_cutoff'] = self.sexcutoff

        if value > self.sexcutoff:
            self.data['predicted_sex'] = 'male'
        else:
            self.data['predicted_sex'] = 'female'

    def predict(self):
        self._predict_sex()
        return self.data
