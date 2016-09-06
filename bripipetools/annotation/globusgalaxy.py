"""
Classify / provide details for objects generated from a Globus
Galaxy workflow processing batch performed by the BRI Bioinformatics
Core.
"""

import logging
logger = logging.getLogger(__name__)

import os
import re
import bripipetools.model as docs
from bripipetools.util import files
from bripipetools.parsing import illumina

class WorkflowBatchAnnotator(object):
    """
    Identifies, stores, and updates information about a workflow batch.
    """
    def __init__(self, workflow_batch_file, genomics_root):
        logger.info("creating an instance of WorkflowBatchAnnotator")
        self.workflow_batch_file = workflow_batch_file
        # self.flowcellrun = self._init_flowcellrun(run_id)

        logger.debug("setting 'genomics' path")
        self.genomics_path = os.path.join(genomics_root, 'genomics')
