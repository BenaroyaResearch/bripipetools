"""
Class and methods to perform routine sex check on all processed libraries.
"""
import logging

from .. import genlims

logger = logging.getLogger(__name__)


class SexVerifier(object):
    """
    Identifies, stores, and updates information about a workflow batch.
    """
    def __init__(self, data, processedlibrary, db):
        logger.debug("creating an instance of SexVerifier")
        self.data = data
        self.processedlibrary = processedlibrary
        self.db = db

    def _retrieve_sex(self, parent_id):
        """
        Retrieve reported sex for sample.
        """
        logger.debug("searching parents of {} for reported sex"
                     .format(parent_id))
        try:
            logger.debug("searching for 'reportedSex' field...")
            return genlims.search_ancestors(
                self.db, parent_id, 'reportedSex'
                ).lower()
        except AttributeError:
            try:
                logger.debug("searching for 'gender' field...")
                return genlims.search_ancestors(
                    self.db, parent_id, 'gender'
                    ).lower()
            except AttributeError:
                logger.debug("reported sex not found")
                return

    def verify(self):
        """
        Compare reported sex for sample to predicted sex of processed
        library.

        :return:
        """
        reported_sex = self._retrieve_sex(self.processedlibrary.parent_id)
        logger.debug("reported sex is {}".format(reported_sex))

        if self.data['predicted_sex'] == reported_sex:
            self.data['sex_check'] = 'pass'
        elif reported_sex is None:
            self.data['sex_check'] = 'NA'
        else:
            self.data['sex_check'] = 'fail'
        return self.data
