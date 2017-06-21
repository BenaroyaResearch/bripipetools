"""
Class for importing data from a sequencing run into GenLIMS as new objects.
"""
import logging

from .. import parsing
from .. import genlims
from .. import annotation

logger = logging.getLogger(__name__)


class FlowcellRunImporter(object):
    """
    Collects FlowcellRun and SequencedLibrary objects from a sequencing run,
    converts to documents, inserts into database.
    """
    def __init__(self, path, db, qc_opts):
        logger.debug("creating `SequencingImporter` instance")
        logger.debug("...with arguments (path: '{}', db: '{}')"
                     .format(path, db.name))
        self.path = path
        self.db = db
        self.qc_opts = qc_opts

    def _collect_flowcellrun(self):
        """
        Collect FlowcellRun object for flowcell run.
        """
        path_items = parsing.parse_flowcell_path(self.path)
        logger.info("collecting info for flowcell run {}"
                    .format(path_items['run_id']))

        return annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            genomics_root=path_items['genomics_root'],
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
            genomics_root=path_items['genomics_root'],
            db=self.db
            ).get_sequenced_libraries()

    def _insert_flowcellrun(self):
        """
        Convert FlowcellRun object and insert into GenLIMS database.
        """
        flowcellrun = self._collect_flowcellrun()
        logger.debug("inserting flowcell run {} into {}"
                     .format(flowcellrun, self.db.name))
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
            logger.info(("Inserting sequenced libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_sequencedlibraries()
        if collection in ['all', 'runs']:
            logger.info("Inserting flowcell run '{}' into '{}'"
                        .format(self.path, self.db.name))
            self._insert_flowcellrun()
