"""
Classify / provide details for objects generated from an Illumina
sequencing run performed by the BRI Genomics Core.
"""
import logging
import os
import re

from .. import parsing
from .. import genlims
from .. import model as docs
from . import SequencedLibraryAnnotator

logger = logging.getLogger(__name__)


class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(self, run_id, genomics_root, db):
        logger.debug("creating `FlowcellRunAnnotator` instance for run ID '{}'"
                     .format(run_id))
        self.run_id = run_id
        self.db = db
        self.flowcellrun = self._init_flowcellrun()

        logger.debug("setting 'genomics' path")
        self.genomics_path = os.path.join(genomics_root, 'genomics')

    def _init_flowcellrun(self):
        """
        Try to retrieve data for the flowcell run from GenLIMS; if
        unsuccessful, create new ``FlowcellRun`` object.
        """
        logger.debug("initializing `FlowcellRun` instance")
        try:
            logger.debug("getting `FlowcellRun` from GenLIMS")
            return genlims.map_to_object(
                genlims.get_runs(self.db, {'_id': self.run_id})[0])
        except IndexError:
            logger.debug("creating new `FlowcellRun` object", exc_info=True)
            return docs.FlowcellRun(_id=self.run_id)

    def get_flowcell_path(self):
        """
        Find path to flowcell folder on the server.
        """
        illumina_path = os.path.join(self.genomics_path, 'Illumina')
        logger.debug("searching for flowcell folder")
        try:
            return [os.path.join(illumina_path, p)
                    for p in os.listdir(illumina_path)
                    if p == self.flowcellrun._id][0]
        except OSError:
            logger.error("'genomics' path '{}' is invalid".format(
                self.genomics_path))
            raise

    def get_unaligned_path(self):
        """
        Find path to unaligned data in flowcell folder.
        """
        logger.debug("searching for 'Unaligned' folder")
        try:
            unaligned_path = os.path.join(self.get_flowcell_path(),
                                          'Unaligned')
            if not os.path.exists(unaligned_path):
                raise OSError
            return unaligned_path
        except OSError:
            logger.error("'Unaligned' folder doesn't exist")
            raise

    def _update_flowcellrun(self):
        """
        Add any missing fields to FlowcellRun object.
        """
        logger.debug("updating `FlowcellRun` object attributes")
        pass

    def get_flowcell_run(self):
        """
        Return flowcell run object with updated fields.
        """
        self._update_flowcellrun()
        logger.debug("returning flowcell run object info: {}".format(
            self.flowcellrun.to_json()))
        return self.flowcellrun

    def get_projects(self):
        """
        Collect list of projects for flowcell run.
        """
        unaligned_path = self.get_unaligned_path()
        logger.debug("collecting list of projects")
        return [p for p in os.listdir(unaligned_path)
                if len(parsing.get_project_label(p))]

    def get_libraries(self, project=None):
        """
        Collect list of libraries for flowcell run from one or all projects.
        """
        unaligned_path = self.get_unaligned_path()
        projects = self.get_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        logger.debug("collecting list of libraries")
        logger.debug("searching in projects {}".format(projects))
        return [l for p in projects
                for l in os.listdir(os.path.join(unaligned_path, p))
                if len(parsing.get_library_id(l))]

    def get_sequenced_libraries(self, project=None):
        """
        Collect sequenced library objects for flowcell run.
        """
        unaligned_path = self.get_unaligned_path()
        projects = self.get_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        sequencedlibraries = []
        for p in projects:
            logger.info("getting sequenced libraries for project '{}'"
                        .format(p))
            libraries = self.get_libraries(p)
            sequencedlibraries += [SequencedLibraryAnnotator(
                        os.path.join(unaligned_path, p, l),
                        l, p, self.run_id, self.db
                        ).get_sequenced_library()
                        for l in libraries]
        return sequencedlibraries
