"""
Class for importing data from a sequencing run into GenLIMS as new objects.
"""
import logging
logger = logging.getLogger(__name__)
import os

from .. import util
from .. import genlims
from .. import annotation

class SequencingImporter(object):
    """
    Collects FlowcellRun and SequencedLibrary objects from a sequencing run,
    converts to documents, inserts into database.
    """
    def __init__(self, path, db):
        logger.info("creating an instance of SequencingImporter")
        logger.debug("...with arguments (path: {}, db: {})"
                     .format(path, db))
        self.path = path
        self.db = db

    def _parse_flowcell_path(self):
        """
        Return 'genomics' root and run ID based on directory path.
        """
        return {'genomics_root': util.matchdefault('.*(?=genomics)', self.path),
                'run_id': os.path.basename(self.path.rstrip('/'))}

    def _collect_flowcellrun(self):
        """
        Collect FlowcellRun object for flowcell run.
        """
        path_items = self._parse_flowcell_path()
        logger.info("collecting info for flowcell run {}"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            genomics_root=path_items['genomics_root'],
            db=self.db
            ).flowcellrun

    def _collect_sequencedlibraries(self):
        """
        Collect list of SequencedLibrary objects for flowcell run.
        """
        path_items = self._parse_flowcell_path()
        logger.info("collecting sequenced libraries for flowcell run {}"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            genomics_root=path_items['genomics_root'],
            db=self.db
            ).get_sequenced_libraries()

    def _insert_flowcellrun(self):
        """
        Convert FlowcellRun object and insert into GenLIMS database.
        """
        flowcellrun = self._collect_flowcellrun()
        logger.debug("inserting flowcell run {}".format(flowcellrun))
        genlims.put_runs(self.db, flowcellrun.to_json())

    def _insert_sequencedlibraries(self):
        """
        Convert SequencedLibrary objects and insert into GenLIMS database.
        """
        sequencedlibraries = self._collect_sequencedlibraries()
        for sl in sequencedlibraries:
            logger.debug("inserting sequenced library {}".format(sl))
            genlims.put_samples(self.db, sl.to_json())

    def insert(self, collection='all'):
        """
        Insert documents into GenLIMS database.
        """
        if collection in ['all', 'samples']:
            self._insert_sequencedlibraries()
        if collection in ['all', 'runs']:
            self._insert_flowcellrun()
