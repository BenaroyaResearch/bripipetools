"""
Classify / provide details for sequenced libraries (outputs of a
flowcell sequencing run) and the associated raw data.
"""
import logging
import os
import re

from .. import parsing
from .. import genlims
from .. import model as docs

logger = logging.getLogger(__name__)


class SequencedLibraryAnnotator(object):
    """
    Identifies, stores, and updates information about a sequenced library.
    """
    def __init__(self, path, library, project, run_id, db):
        logger.debug("creating `SequencedLibraryAnnotator` instance "
                     "for library '{}'".format(library))
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
        logger.debug("initializing `SequencedLibrary` instance")
        try:
            logger.debug("getting `SequencedLibrary` from GenLIMS")
            return genlims.map_to_object(
                genlims.get_samples(self.db, {'_id': self.seqlib_id})[0])
        except IndexError:
            logger.debug("creating new `SequencedLibrary` object")
            return docs.SequencedLibrary(_id=self.seqlib_id)

    def _get_raw_data(self):
        """
        Locate and store details about raw data for sequenced library.
        """
        logger.debug("collecting raw data details for library '{}'"
                     .format(self.library_id))
        return [parsing.parse_fastq_filename(f)
                for f in os.listdir(self.path)
                if not re.search('empty', f)]

    def _update_sequencedlibrary(self):
        """
        Add any missing fields to SequencedLibrary object.
        """
        logger.debug("updating `SequencedLibrary` object attributes")

        project_items = parsing.parse_project_label(self.project_label)
        update_fields = {'project_id': project_items['project_id'],
                         'subproject_id': project_items['subproject_id'],
                         'run_id': self.run_id,
                         'parent_id': self.library_id,
                         'raw_data': self._get_raw_data()}
        self.sequencedlibrary.is_mapped = False
        self.sequencedlibrary.update_attrs(update_fields, force=True)

    def get_sequenced_library(self):
        """
        Return sequenced library object with updated fields.
        """
        self._update_sequencedlibrary()
        logger.debug("returning sequenced library object info: {}".format(
            self.sequencedlibrary.__dict__)
        )
        return self.sequencedlibrary
