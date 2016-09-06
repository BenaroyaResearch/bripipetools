"""
Classify / provide details for objects generated from a Globus
Galaxy workflow processing batch performed by the BRI Bioinformatics
Core.
"""

import logging
logger = logging.getLogger(__name__)

import os
import re
import datetime
from bripipetools import io
import bripipetools.model as docs
from bripipetools.util import files
from bripipetools.parsing import illumina

class WorkflowBatchAnnotator(object):
    """
    Identifies, stores, and updates information about a workflow batch.
    """
    def __init__(self, workflowbatch_file, genomics_root):
        logger.info("creating an instance of WorkflowBatchAnnotator")
        self.workflowbatch_file = workflowbatch_file
        self.workflowbatch_data = io.WorkflowBatchFile(
            self.workflowbatch_file,
            state='submit'
            ).parse()

        batch_items = self._parse_batch_name(
            self.workflowbatch_data['batch_name']
        )
        self.date = batch_items['date']
        self.projects = batch_items['projects']
        self.flowcell_id = batch_items['flowcell_id']

        logger.debug("setting 'genomics' path")
        self.genomics_path = os.path.join(genomics_root, 'genomics')

    def _parse_batch_name(self, batch_name):
        """
        Parse batch name indicated in workflow batch submit file and
        return individual components indicating date, list of project
        labels, and flowcell ID.
        """
        name_parts = batch_name.split('_')
        d = datetime.datetime.strptime(name_parts.pop(0), '%y%m%d')
        date = datetime.date.isoformat(d)

        fc_id = name_parts.pop(-1)

        return {'date': date, 'projects': name_parts, 'flowcell_id': fc_id}

    def _init_workflowbatch(self, workflowbatch_file, workflow_id, date):
        """
        Try to retrieve data for the workflow batch from GenLIMS; if
        unsuccessful, create new ``GalaxyWorkflowBatch`` object.
        """
        logger.info("initializing GalaxyWorkflowBatch instance")
        try:
            logger.debug("getting GalaxyWorkflowBatch from GenLIMS")
            return genlims.get_workflowbatch(
                workflowbatch_file=workflowbatch_file
                )
        except NameError:
            logger.debug("creating new GalaxyWorkflowBatch object")
            num = 1
            workflowbatch_id = 'globusgalaxy_{}_{}'.format(date, num)
            # return docs.GalaxyWorkflowBatch(_id=run_id)
