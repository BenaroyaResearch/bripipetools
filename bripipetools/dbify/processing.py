"""
Class for importing data from a processing batch into GenLIMS as new objects.
"""
import logging
import os

from .. import util
from .. import genlims
from .. import annotation

logger = logging.getLogger(__name__)


class ProcessingImporter(object):
    """
    Collects WorkflowBatch and ProcessedLibrary objects from a processing
    batch, converts to documents, inserts into database.
    """
    def __init__(self, path, db):
        logger.debug("creating an instance of ProcessingImporter")
        logger.debug("...with arguments (path: {}, db: {})"
                     .format(path, db.name))
        self.path = path
        self.db = db

    def _parse_batch_file_path(self):
        """
        Return 'genomics' root and batch file name based on directory path.
        """
        return {'genomics_root': util.matchdefault('.*(?=genomics)', self.path),
                'workflowbatch_filename': os.path.basename(self.path)}

    def _collect_workflowbatch(self):
        """
        Collect WorkflowBatch object for flowcell run.
        """
        path_items = self._parse_batch_file_path()
        logger.info("collecting info for workflow batch file {}"
                    .format(path_items['workflowbatch_filename']))

        return annotation.WorkflowBatchAnnotator(
            workflowbatch_file=self.path,
            genomics_root=path_items['genomics_root'],
            db=self.db
            ).get_workflow_batch()

    def _collect_processedlibraries(self):
        """
        Collect list of ProcessedLibrary objects for flowcell run.
        """
        path_items = self._parse_batch_file_path()
        logger.info("collecting sequenced libraries for workflow batch file {}"
                    .format(path_items['workflowbatch_filename']))

        return annotation.WorkflowBatchAnnotator(
            workflowbatch_file=self.path,
            genomics_root=path_items['genomics_root'],
            db=self.db
            ).get_processed_libraries(qc=False)

    def _insert_workflowbatch(self):
        """
        Convert WorkflowBatch object and insert into GenLIMS database.
        """
        workflowbatch = self._collect_workflowbatch()
        logger.debug("inserting workflow batch {}".format(workflowbatch))
        genlims.put_workflowbatches(self.db, workflowbatch.to_json())

    def _insert_processedlibraries(self):
        """
        Convert ProcessedLibrary objects and insert into GenLIMS database.
        """
        processedlibraries = self._collect_processedlibraries()
        for pl in processedlibraries:
            logger.debug("inserting processed library {}".format(pl))
            genlims.put_samples(self.db, pl.to_json())

    def insert(self, collection='all'):
        """
        Insert documents into GenLIMS database.
        """
        if collection in ['all', 'samples']:
            self._insert_processedlibraries()
        if collection in ['all', 'workflowbatches']:
            self._insert_workflowbatch()
