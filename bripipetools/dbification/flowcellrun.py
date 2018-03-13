"""
Class for importing data from a sequencing run into GenLIMS as new objects.
"""
import logging

from .. import parsing
from .. import genlims
from .. import researchdb
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
            genomics_root=path_items['genomics_root'],
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
            genomics_root=path_items['genomics_root'],
            db=self.db
            ).get_library_metrics()

    def _insert_flowcellrun(self, collection='all'):
        """
        Convert FlowcellRun object and insert into GenLIMS database.
        """
        flowcellrun = self._collect_flowcellrun()
        logger.debug("inserting flowcell run {} into {}"
                     .format(flowcellrun, self.db.name))
        if collection == 'researchdb':
            researchdb.put_runs(self.db, flowcellrun.to_json())
        else:
            genlims.put_runs(self.db, flowcellrun.to_json())

    def _insert_sequencedlibraries(self, collection='all'):
        """
        Convert SequencedLibrary objects and insert into GenLIMS database.
        """
        sequencedlibraries = self._collect_sequencedlibraries()
        for sl in sequencedlibraries:
            logger.debug("inserting sequenced library {}".format(sl))
            if collection == 'researchdb':
                researchdb.put_samples(self.db, sl.to_json())
            else:
                genlims.put_samples(self.db, sl.to_json())

    def _insert_librarygenecounts(self, collection='researchdb'):
        """
        Convert Library Results objects and insert into Research database.
        """
        librarygenecounts = self._collect_librarygenecounts()
        for lgc in librarygenecounts:
            logger.debug("inserting library gene counts '{}'".format(lgc))
            if collection == 'researchdb':
                researchdb.put_counts(self.db, lgc.to_json())
            else:
                genlims.put_counts(self.db, lgc.to_json())

    def _insert_librarymetrics(self, collection='researchdb'):
        """
        Convert Library Results objects and insert into Research database.
        """
        librarymetrics = self._collect_librarymetrics()
        for lgc in librarymetrics:
            logger.debug("inserting library metrics '{}'".format(lgc))
            if collection == 'researchdb':
                researchdb.put_metrics(self.db, lgc.to_json())
            else:
                genlims.put_metrics(self.db, lgc.to_json())

    def insert(self, collection='all'):
        """
        Insert documents into GenLIMS or ResearchDB databases.
        """
        if collection in ['all', 'researchdb', 'samples']:
            logger.info(("Inserting sequenced libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_sequencedlibraries(collection)
            
        if collection in ['researchdb', 'counts']:
            logger.info(("Inserting gene counts for libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_librarygenecounts(collection)
            
        if collection in ['researchdb', 'metrics']:
            logger.info(("Inserting metrics for libraries for flowcell '{}' "
                         "into '{}'").format(self.path, self.db.name))
            self._insert_librarymetrics(collection)

        if collection in ['all', 'researchdb', 'flowcell', 'runs']:
            logger.info("Inserting flowcell run '{}' into '{}'"
                        .format(self.path, self.db.name))
            self._insert_flowcellrun(collection)
