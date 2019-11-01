"""
Classify / provide details for objects generated from an Illumina
sequencing run performed by the BRI Genomics Core.
"""
import logging
import os
import re

from .. import parsing
from .. import database
from .. import model as docs
from . import SequencedLibraryAnnotator
from . import LibraryGeneCountAnnotator
from . import LibraryMetricsAnnotator

logger = logging.getLogger(__name__)


class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(self, run_id, pipeline_root, db):
        logger.debug("creating `FlowcellRunAnnotator` instance for run ID '{}'"
                     .format(run_id))
        self.run_id = run_id
        self.db = db
        self.flowcellrun = self._init_flowcellrun()

        logger.debug("setting 'pipeline' path")
        self.pipeline_path = os.path.join(pipeline_root, 'pipeline')

    def _init_flowcellrun(self):
        """
        Try to retrieve data for the flowcell run from GenLIMS; if
        unsuccessful, create new ``FlowcellRun`` object.
        """
        logger.debug("initializing `FlowcellRun` instance")
        try:
            logger.debug("getting `FlowcellRun` from GenLIMS")
            return database.map_to_object(
                database.get_genomicsRuns(self.db, {'_id': self.run_id})[0])
        except IndexError:
            logger.debug("creating new `FlowcellRun` object", exc_info=True)
            return docs.FlowcellRun(_id=self.run_id)

    def get_flowcell_path(self):
        """
        Find path to flowcell folder on the server.
        """
        illumina_path = os.path.join(self.pipeline_path, 'Illumina')
        logger.debug("searching for flowcell folder")
        try:
            return [os.path.join(illumina_path, p)
                    for p in os.listdir(illumina_path)
                    if p == self.flowcellrun._id][0]
        except OSError:
            logger.error("'pipeline' path '{}' is invalid".format(
                self.pipeline_path))
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

    def get_processed_projects(self):
        """
        List processed projects for a flowcell run.
        """
        flowcell_path = self.get_flowcell_path()
        return (pp
            for pp in os.listdir(flowcell_path)
            if re.search('Project_.*Processed', pp))

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
        # Need to handle possibility of new basespace directory structure
        libList = []
        for p in projects:
            logger.debug("Attempting to collect libs for project: {}".format(p))
            for l in os.listdir(os.path.join(unaligned_path, p)):
                logger.debug("Looking for lib name in: {}".format(l))
                # Old basespace - able to parse libid from current dir
                if (len(parsing.get_library_id(l))):
                    libList.append(l)
                # New basespace - need to go down one more level to parse lib
                elif (os.path.isdir(os.path.join(unaligned_path, p, l))): 
                    logger.debug("Lib name not found. Going down into: {}"
                                .format(os.path.join(unaligned_path, p, l)))
                    for lNext in os.listdir(os.path.join(unaligned_path, p, l)):
                        if (len(parsing.get_library_id(lNext))):
                            libList.append(os.path.join(l,lNext))
                else:
                    logger.debug("Lib name not found and {} is not a directory."
                                .format(os.path.join(unaligned_path, p, l)))
        
        return libList

    def get_processed_libraries(self, project=None, sub_path="inputFastqs"):
        """
        Collect list of libraries for flowcell run from one or all projects.
        """
        flowcell_path = self.get_flowcell_path()
        projects = self.get_processed_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        logger.debug("collecting list of libraries")
        logger.debug("searching in projects {}".format(projects))
        return [l for p in projects
                for l in os.listdir(os.path.join(flowcell_path, p, sub_path))
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
    
    def get_library_gene_counts(self, project=None):
        """
        Collect library gene count objects for flowcell run.
        """

        projects = self.get_processed_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        librarygenecounts = []
        for p in projects:
            logger.info("getting library gene counts for project '{}'"
                        .format(p))
            libraries = self.get_processed_libraries(p)
            #logger.info("getting libraries '{}'".format(libraries))

            librarygenecounts += [LibraryGeneCountAnnotator(
                        os.path.join(self.get_flowcell_path(), p),
                        l, p, self.run_id, self.db
                        ).get_library_gene_counts()
                        for l in libraries]
        return librarygenecounts
    
    def get_library_metrics(self, project=None):
        """
        Collect library gene count objects for flowcell run.
        """

        projects = self.get_processed_projects()
        if project is not None:
            logger.debug("subsetting projects")
            projects = [p for p in projects
                        if re.search(project, p)]
        librarymetrics = []
        for p in projects:
            logger.info("getting library metrics for project '{}'"
                        .format(p))
            libraries = self.get_processed_libraries(p)
            #logger.info("getting libraries '{}'".format(libraries))

            librarymetrics += [LibraryMetricsAnnotator(
                        os.path.join(self.get_flowcell_path(), p),
                        l, p, self.run_id, self.db
                        ).get_library_metrics()
                        for l in libraries]
        return librarymetrics

