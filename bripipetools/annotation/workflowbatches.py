"""
Classify / provide details for objects generated from a Globus
Galaxy workflow processing batch performed by the BRI Bioinformatics
Core.
"""
import logging
import os
import datetime

from .. import util
from .. import parsing
from .. import io
from .. import genlims
from .. import qc
from .. import model as docs
from . import ProcessedLibraryAnnotator

logger = logging.getLogger(__name__)


class WorkflowBatchAnnotator(object):
    """
    Identifies, stores, and updates information about a workflow batch.
    """
    def __init__(self, workflowbatch_file, genomics_root, db):
        logger.debug("creating `WorkflowBatchAnnotator` for '{}'"
                     .format(workflowbatch_file))
        self.workflowbatch_file = workflowbatch_file
        self.db = db

        self.workflowbatch_data = io.WorkflowBatchFile(
            self.workflowbatch_file,
            state='submit'
            ).parse()
        self.workflowbatch = self._init_workflowbatch()

        logger.debug("setting 'genomics' path")
        self.genomics_root = genomics_root
        self.genomics_path = os.path.join(genomics_root, 'genomics')

    def _init_workflowbatch(self):
        """
        Try to retrieve data for the workflow batch from GenLIMS; if
        unsuccessful, create new ``GalaxyWorkflowBatch`` object.
        """
        logger.debug("initializing `GalaxyWorkflowBatch` instance")
        workflowbatch_file = util.swap_root(self.workflowbatch_file,
                                            'genomics', '/')

        try:
            logger.debug("getting `GalaxyWorkflowBatch` from GenLIMS; "
                         "searching for record with batch file '{}'"
                         .format(workflowbatch_file))
            return genlims.map_to_object(
                genlims.get_workflowbatches(
                    self.db,
                    {'workflowbatchFile': workflowbatch_file}
                )[0]
            )
        except IndexError:
            logger.debug("creating new `GalaxyWorkflowBatch` object",
                         exc_info=True)

            batch_items = parsing.parse_batch_name(
                self.workflowbatch_data['batch_name']
            )

            workflowbatch_id = genlims.create_workflowbatch_id(
                db=self.db,
                prefix='globusgalaxy',
                date=batch_items['date']
            )
            return docs.GalaxyWorkflowBatch(
                _id=workflowbatch_id,
                workflowbatch_file=workflowbatch_file
            )

    def _update_workflowbatch(self):
        """
        Add any missing fields to GalaxyWorkflowBatch object.
        """
        logger.debug("updating `GalaxyWorkflowBatch` object attributes")

        batch_items = parsing.parse_batch_name(
            self.workflowbatch_data['batch_name']
        )

        update_fields = {
            'workflow_id': self.workflowbatch_data['workflow_name'],
            'date': batch_items['date'],
            'projects': batch_items['projects'],
            'flowcell_id': batch_items['flowcell_id']
        }
        self.workflowbatch.is_mapped = False
        self.workflowbatch.update_attrs(update_fields, force=True)

    def get_workflow_batch(self):
        """
        Return workflow batch object with updated fields.
        """
        self._update_workflowbatch()
        logger.debug("returning workflow batch object info: {}"
                     .format(self.workflowbatch.to_json()))
        return self.workflowbatch

    def get_sequenced_libraries(self):
        """
        Collect list of sequenced libraries processed as part of
        workflow batch.
        """
        return [p['value']
                for s in self.workflowbatch_data['samples']
                for p in s
                if p['name'] == 'SampleName']

    def _check_sex(self, processedlibrary):
        """
        Retrieve reported sex for sample and compare to predicted sex
        of processed library.
        """
        ref = util.matchdefault('(grch38|ncbim37)',
                                self.workflowbatch_data['workflow_name'])
        if ref != 'grch38':
            return processedlibrary

        logger.debug("adding sex check QC info for processed library '{}'"
                     .format(processedlibrary._id))
        sexchecker = qc.SexChecker(
            processedlibrary=processedlibrary,
            reference=ref,
            workflowbatch_id=self.workflowbatch._id,
            genomics_root=self.genomics_root,
            db=self.db
        )
        return sexchecker.update()

    def get_processed_libraries(self, project=None, qc=False):
        """
        Collect processed library objects for workflow batch.
        """
        workflowbatch_id = self.workflowbatch._id
        logger.debug("getting processed libraries for workflow batch '{}'"
                     .format(workflowbatch_id))

        return [
            ProcessedLibraryAnnotator(
                workflowbatch_id, sample_params, self.db
            ).get_processed_library()
            if not qc else self._check_sex(
                ProcessedLibraryAnnotator(
                    workflowbatch_id, sample_params, self.db
                ).get_processed_library()
            ) for sample_params in self.workflowbatch_data['samples']
            ]



