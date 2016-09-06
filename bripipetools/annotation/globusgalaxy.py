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
from bripipetools import genlims
from bripipetools.model import documents as docs
from bripipetools.util import files
from bripipetools.parsing import illumina

class WorkflowBatchAnnotator(object):
    """
    Identifies, stores, and updates information about a workflow batch.
    """
    def __init__(self, workflowbatch_file, db, genomics_root):
        logger.info("creating an instance of WorkflowBatchAnnotator")
        self.workflowbatch_file = workflowbatch_file
        self.db = db

        self.workflowbatch_data = io.WorkflowBatchFile(
            self.workflowbatch_file,
            state='submit'
            ).parse()
        self.workflowbatch = self._init_workflowbatch()

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

    def _init_workflowbatch(self):
        """
        Try to retrieve data for the workflow batch from GenLIMS; if
        unsuccessful, create new ``GalaxyWorkflowBatch`` object.
        """
        logger.info("initializing GalaxyWorkflowBatch instance")
        workflowbatch_file = files.swap_root(self.workflowbatch_file,
                                            'genomics', '/')
        try:
            logger.debug("getting GalaxyWorkflowBatch from GenLIMS; "
                         "searching for record with batch file {}"
                         .format(workflowbatch_file))
            return genlims.get_workflowbatches(self.db,
                {'workflowbatchFile': workflowbatch_file}
                )[0]
        except IndexError:
            logger.debug("creating new GalaxyWorkflowBatch object",
                         exc_info=True)

            batch_items = self._parse_batch_name(
                self.workflowbatch_data['batch_name']
            )

            workflowbatch_id = genlims.create_workflowbatch_id(
                db = self.db,
                prefix = 'globusgalaxy',
                date = batch_items['date']
            )
            return docs.GalaxyWorkflowBatch(
                _id=workflowbatch_id,
                workflowbatch_file=workflowbatch_file
            )

    def _update_workflowbatch(self):
        """
        Add any missing fields to GalaxyWorkflowBatch object.
        """
        logger.debug("updating GalaxyWorkflowBatch object attributes")

        batch_items = self._parse_batch_name(
            self.workflowbatch_data['batch_name']
        )

        # self.workflowbatch.workflow_id = self.workflowbatch_data['workflow_name']
        self.workflowbatch.date = batch_items['date']
        self.workflowbatch.projects = batch_items['projects']
        self.workflowbatch.flowcell_id = batch_items['flowcell_id']
