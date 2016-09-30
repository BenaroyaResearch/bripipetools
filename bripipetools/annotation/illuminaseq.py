"""
Classify / provide details for objects generated from an Illumina
sequencing run performed by the BRI Genomics Core.
"""
import logging
logger = logging.getLogger(__name__)
import os
import re

from .. import util
from .. import parsing
from .. import genlims
from .. import model as docs

class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(self, run_id, genomics_root, db):
        logger.info("creating instance of FlowcellRunAnnotator for run ID {}"
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
        logger.info("initializing FlowcellRun instance")
        try:
            logger.debug("getting FlowcellRun from GenLIMS")
            return genlims.map_to_object(
                genlims.get_runs(self.db, {'_id': self.run_id})[0])
        except IndexError:
            logger.debug("creating new FlowcellRun object", exc_info=True)
            return docs.FlowcellRun(_id=self.run_id)

    def _get_flowcell_path(self):
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

    def _get_unaligned_path(self):
        """
        Find path to unaligned data in flowcell folder.
        """
        try:
            return os.path.join(self._get_flowcell_path(), 'Unaligned')
        except OSError:
            logger.error("'Unaligned' folder doesn't exist")
            raise

    def get_projects(self):
        """
        Collect list of projects for flowcell run.
        """
        unaligned_path = self._get_unaligned_path()
        logger.info("collecting list of projects")
        return [p for p in os.listdir(unaligned_path)
                if len(parsing.get_project_label(p))]

    def get_libraries(self, project=None):
        """
        Collect list of libraries for flowcell run from one or all projects.
        """
        unaligned_path = self._get_unaligned_path()
        projects = self.get_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        logger.info("collecting list of libraries")
        logger.debug("searching in projects {}".format(projects))
        return [l for p in projects
                for l in os.listdir(os.path.join(unaligned_path, p))
                if len(parsing.get_library_id(l))]

    def get_sequenced_libraries(self, project=None):
        """
        Collect sequenced library objects for flowcell run.
        """
        unaligned_path = self._get_unaligned_path()
        projects = self.get_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        sequencedlibraries = []
        for p in projects:
            logger.info("getting sequenced libraries for project {}".format(p))
            libraries = self.get_libraries(p)
            sequencedlibraries += [SequencedLibraryAnnotator(
                        os.path.join(unaligned_path, p, l),
                        l, p, self.run_id, self.db
                        ).get_sequenced_library()
                        for l in libraries]
        return sequencedlibraries


class SequencedLibraryAnnotator(object):
    """
    Identifies, stores, and updates information about a sequenced library.
    """
    def __init__(self, path, library, project, run_id, db):
        logger.info("creating an instance of SequencedLibraryAnnotator "
                    "for library {}".format(library))
        self.path = path
        self.db = db
        self.library_id = parsing.get_library_id(library)
        self.project_label = parsing.get_project_label(project)
        self.run_id = run_id
        self.run_items = parsing.parse_flowcell_run_id(run_id)
        self.seqlib_id = '{}_{}'.format(self.library_id,
                                        self.run_items['flowcell_id'])
        self.sequencedlibrary = self._init_sequencedlibrary()

    def _init_sequencedlibrary(self):
        """
        Try to retrieve data for the sequenced library from GenLIMS;
        if unsuccessful, create new ``SequencedLibrary`` object.
        """
        logger.info("initializing SequencedLibrary instance")
        try:
            logger.debug("getting SequencedLibrary from GenLIMS")
            return genlims.map_to_object(
                genlims.get_samples(self.db, {'_id': self.seqlib_id})[0])
        except IndexError:
            logger.debug("creating new SequencedLibrary object")
            return docs.SequencedLibrary(_id=self.seqlib_id)

    def _get_raw_data(self):
        """
        Locate and store details about raw data for sequenced library.
        """
        logger.debug("collecting raw data details for library {}".format(
            self.library_id))
        return [parsing.parse_fastq_filename(f)
                for f in os.listdir(self.path)
                if not re.search('empty', f)]

    def _update_sequencedlibrary(self):
        """
        Add any missing fields to SequencedLibrary object.
        """
        logger.debug("updating SequencedLibrary object attributes")

        project_items = parsing.parse_project_label(self.project_label)
        self.sequencedlibrary.project_id = project_items['project_id']
        self.sequencedlibrary.subproject_id = project_items['subproject_id']
        self.sequencedlibrary.run_id = self.run_id
        self.sequencedlibrary.parent_id = self.library_id
        self.sequencedlibrary.raw_data = self._get_raw_data()

    def get_sequenced_library(self):
        """
        Return sequenced library object with updated fields.
        """
        self._update_sequencedlibrary()
        logger.debug("returning sequenced library object: {}".format(
            self.sequencedlibrary.__dict__))
        return self.sequencedlibrary
