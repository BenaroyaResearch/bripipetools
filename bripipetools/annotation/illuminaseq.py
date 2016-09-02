"""
Classify / provide details for objects generated from an Illumina
sequencing run performed by the BRI Genomics Core.
"""

import logging
logger = logging.getLogger(__name__)

import os
import re
import bripipetools.model as docs
from bripipetools.util import files
from bripipetools.parsing import illumina

class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(self, run_id, genomics_root):
        logger.info("creating an instance of FlowcellRunAnnotator")
        self.run_id = run_id
        self.flowcellrun = self._init_flowcellrun(run_id)

        logger.debug("setting 'genomics' path")
        self.genomics_path = os.path.join(genomics_root, 'genomics')

    def _init_flowcellrun(self, run_id):
        """
        Try to retrieve data for the flowcell run from GenLIMS; if
        unsuccessful, create new ``FlowcellRun`` object.
        """
        logger.info("initializing FlowcellRun instance")
        try:
            logger.debug("getting FlowcellRun from GenLIMS")
            return genlims.get_run(_id=run_id)
        except:
            logger.debug("creating new FlowcellRun object")
            return docs.FlowcellRun(_id=run_id)

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
                self.genomics_path
            ))
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
        return [p
                for p in os.listdir(unaligned_path)
                if len(illumina.get_project_label(p))]

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
                if len(illumina.get_lib_id(l))]

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
        for p in projects:
            logger.info("getting sequenced libraries for project {}".format(p))
            libraries = self.get_libraries(p)


class SequencedLibraryAnnotator(object):
    """
    Identifies, stores, and updates information about a sequenced library.
    """
    def __init__(self, path):
        logger.info("creating an instance of SequencedLibraryAnnotator")
        self.path = path
