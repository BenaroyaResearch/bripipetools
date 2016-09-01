
import logging
logger = logging.getLogger(__name__)

import os
import re
import bripipetools.model as docs
from bripipetools.util import files

class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(self, run_id, genomics_root=None):
        logger.info("creating an instance of FlowcellRunAnnotator")
        self.run_id = run_id
        self.flowcellrun = self._init_flowcellrun(run_id)

        if genomics_root is None:
            logger.debug("locating 'genomics' root")
            genomics_root = self._get_genomics_root()

        logger.debug("setting 'genomics' path")

        try:
            self.genomics_path = os.path.join(genomics_root, 'genomics')
        except AttributeError:
            logger.error("Failed to locate 'genomics' root", exc_info=True)
            raise

    def _init_flowcellrun(self, run_id):
        """
        Try to retrieve data for the flowcell run from GenLIMS; if
        unsuccessful, create new ``FlowcellRun`` object.
        """
        try:
            return genlims.get_run(_id=run_id)
        except:
            return docs.FlowcellRun(_id=run_id)

    def _get_genomics_root(self):
        """
        Locate the root directory preceding 'genomics' in the system
        path.
        """
        return files.locate_root_folder('genomics')

    def _get_flowcell_path(self):
        """
        Find path to flowcell folder on the server.
        """
        illumina_path = os.path.join(self.genomics_path, 'Illumina')
        try:
            return [os.path.join(illumina_path, p)
                    for p in os.listdir(illumina_path)
                    if p == self.flowcellrun._id][0]
        except OSError:
            logger.error("'genomics' path '{}' is invalid".format(
                self.genomics_path
            ))
            raise

    # def _get_unaligned_folder(self):
