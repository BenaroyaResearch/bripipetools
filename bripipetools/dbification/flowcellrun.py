"""
Class for importing data from a sequencing run into GenLIMS and the 
Research DB as new objects.
"""
import logging
import os
import re

from .. import parsing
from .. import database
from .. import annotation

logger = logging.getLogger(__name__)


class FlowcellRunImporter(object):
    """
    Collects FlowcellRun and SequencedLibrary objects from a sequencing run,
    converts to documents, inserts into database.
    """
    def __init__(self, path, db, run_opts):
        logger.debug("creating `SequencingImporter` instance")
        logger.debug("...with arguments (path: '{}', db: '{}')"
                     .format(path, db.name))
        self.path = path
        self.db = db
        self.run_opts = run_opts

    def _collect_flowcellrun(self):
        """
        Collect FlowcellRun object for flowcell run.
        """
        path_items = parsing.parse_flowcell_path(self.path)
        logger.info("collecting info for flowcell run {}"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            pipeline_root=path_items['pipeline_root'],
            db=self.db
            ).get_flowcell_run()

    def _collect_sequencedlibraries(self):
        """
        Collect list of SequencedLibrary objects for flowcell run.
        """
        path_items = parsing.parse_flowcell_path(self.path)
        logger.info("Collecting sequenced libraries for flowcell run '{}'"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            pipeline_root=path_items['pipeline_root'],
            db=self.db
            ).get_sequenced_libraries()

    def _collect_librarygenecounts(self):
        """
        Collect list of library gene count objects for flowcell run.
        """
        path_items = parsing.parse_flowcell_path(self.path)
#        print("path: {}, items: {}".format(self.path, path_items))
        logger.info("Collecting library gene counts for flowcell run '{}'"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            pipeline_root=path_items['pipeline_root'],
            db=self.db
            ).get_library_gene_counts()

    def _collect_librarymetrics(self):
        """
        Collect list of library metrics objects for flowcell run.
        """
        path_items = parsing.parse_flowcell_path(self.path)
#        print("path: {}, items: {}".format(self.path, path_items))
        logger.info("Collecting library metrics for flowcell run '{}'"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            pipeline_root=path_items['pipeline_root'],
            db=self.db
            ).get_library_metrics()
            
    def _collect_flowcell_workflowbatches(self):
        """
        Collect WorkflowBatch objects for flowcell run.
        """
        path_items = parsing.parse_flowcell_path(self.path)
        batchfile_dir = os.path.join(self.path, "globus_batch_submission")
        logger.info("collecting info for workflow batch files in '{}'"
                    .format(batchfile_dir))

        return [annotation.WorkflowBatchAnnotator(
            workflowbatch_file=os.path.join(batchfile_dir, curr_batchfile),
            pipeline_root=path_items['pipeline_root'],
            db=self.db,
            run_opts = self.run_opts
            ).get_workflow_batch() 
            for curr_batchfile in os.listdir(batchfile_dir)
            if not re.search('DS_Store', curr_batchfile)]

    def _insert_flowcellrun(self, collection='all'):
        """
        Convert FlowcellRun object and insert into GenLIMS database.
        """
        flowcellrun = self._collect_flowcellrun()
        logger.debug("inserting flowcell run {} into {}"
                     .format(flowcellrun, self.db.name))
        database.put_runs(self.db, flowcellrun.to_json())

    def _insert_sequencedlibraries(self):
        """
        Convert SequencedLibrary objects and insert into GenLIMS database.
        """
        sequencedlibraries = self._collect_sequencedlibraries()
        for sl in sequencedlibraries:
            logger.debug("inserting sequenced library {}".format(sl))
            database.put_samples(self.db, sl.to_json())
    
    def _insert_genomicsSequencedlibraries(self):
        """
        Convert SequencedLibrary objects and insert into Research database.
        """
        sequencedlibraries = self._collect_sequencedlibraries()
        for sl in sequencedlibraries:
            logger.debug("inserting sequenced library {}".format(sl))
            database.put_genomicsSamples(self.db, sl.to_json())

    def _insert_librarygenecounts(self):
        """
        Convert Library Results objects and insert into Research database.
        """
        librarygenecounts = self._collect_librarygenecounts()
        for lgc in librarygenecounts:
            logger.debug("inserting library gene counts '{}'".format(lgc))
            database.put_genomicsCounts(self.db, lgc.to_json())

    def _insert_librarymetrics(self):
        """
        Convert Library Results objects and insert into GenLIMS database.
        """
        librarymetrics = self._collect_librarymetrics()
        for lgc in librarymetrics:
            logger.debug("inserting library metrics '{}'".format(lgc))
            database.put_metrics(self.db, lgc.to_json())
            
    def _insert_genomicsLibrarymetrics(self):
        """
        Convert Library Results objects and insert into Research database.
        """
        librarymetrics = self._collect_librarymetrics()
        for lgc in librarymetrics:
            logger.debug("inserting library metrics '{}'".format(lgc))
            database.put_genomicsMetrics(self.db, lgc.to_json())
    
    def _insert_genomicsWorkflowbatches(self):
        """
        Collect WorkflowBatch objects and insert them into database.
        """
        workflowbatches = self._collect_flowcell_workflowbatches()
        for workflowbatch in workflowbatches:
            logger.debug("inserting workflow batch '{}'".format(workflowbatch))
            database.put_genomicsWorkflowbatches(self.db, workflowbatch.to_json())

    def insert(self, collection='genlims'):
        """
        Insert documents into GenLIMS or ResearchDB databases.
        Note that ResearchDB collections are prepended by 'genomics'
        to indicate the data origin.
        """
        
        # Sample information into ResDB/GenLIMS
        if collection in ['all', 'researchdb', 'genomicsSamples']:
            logger.info(("Inserting sequenced libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_genomicsSequencedlibraries()
        
        if collection in ['all', 'genlims', 'samples']:
            logger.info(("Inserting sequenced libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_sequencedlibraries()
        
        # Gene counts - only into ResDB
        if collection in ['all', 'researchdb', 'genomicsCounts']:
            logger.info(("Inserting gene counts for libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_librarygenecounts()
        
        # Metrics information - only into ResDB
        if collection in ['all', 'researchdb', 'genomicsMetrics']:
            logger.info(("Inserting metrics for libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_genomicsLibrarymetrics()
        
        # Workflow Batch files - only into ResDB
        if collection in ['all', 'researchdb', 'genomicsWorkflowbatches']:
            logger.info(("Inserting workflow batches for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_genomicsWorkflowbatches()

        # Run information into GenLIMS
        if collection in ['all', 'genlims', 'flowcell', 'runs']:
            logger.info("Inserting flowcell run '{}' into '{}'"
                        .format(self.path, self.db.name))
            self._insert_flowcellrun()
