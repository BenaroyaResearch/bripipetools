"""
Get/Insert library gene counts
"""
import logging
import os
import re

from .. import parsing
from .. import genlims
from .. import postprocessing
from .. import model as docs

logger = logging.getLogger(__name__)


class LibraryGeneCountAnnotator(object):
    """
    Identifies, stores, and updates information about library gene counts.
    """
    def __init__(self, path, library, project, run_id, db):
        logger.debug("creating `LibraryGeneCountAnnotator` instance "
                     "for path '{}' project '{}' library '{}'".format(path, project, library))
        self.path = path
        self.db = db
        self.library_id = parsing.get_library_id(library)
        self.run_id = run_id
        self.run_items = parsing.parse_flowcell_run_id(run_id)
        self.seqlib_id = '{}_{}'.format(self.library_id, self.run_items['flowcell_id'])
        self.librarycounts = self._init_librarycounts()

    def _init_librarycounts(self):
        """
        Try to retrieve data for the sequenced library from ResearchDatabase;
        if unsuccessful, create new ``GeneCounts`` object.
        """
        logger.debug("initializing `GeneCounts` instance")
        try:
            logger.debug("getting `GeneCounts` from ResearchDatabase")
            return genlims.map_to_object(
                genlims.get_counts(self.db, {'_id': self.seqlib_id})[0])
        except IndexError:
            logger.debug("creating new `GeneCounts` object")
            return docs.GeneCounts(_id=self.seqlib_id)

    def _update_librarycounts(self):
        """
        Add any missing fields to SequencedLibrary object.
        """
        logger.debug("updating `GeneCounts` object attributes")
        path = os.path.join(self.path, 'counts')
        genecounts = postprocessing.OutputReader(path).read_data(self.seqlib_id)
        #logger.info("library counts: {}".format(librarycounts))
#        logger.info("counts: {}".format(librarycounts))
#        project_items = parsing.parse_project_label(self.project_label)
#         update_fields = {'project_id': project_items['project_id'],
#                          'subproject_id': project_items['subproject_id'],
#                          'run_id': self.run_id,
#                          'parent_id': self.library_id}
        self.librarycounts.is_mapped = False
        self.librarycounts.update_attrs({'gene_counts': genecounts}, force=True)

    def get_library_gene_counts(self):
        """
        Return sequenced library object with updated fields.
        """
        self._update_librarycounts()
        logger.debug("returning sequenced library object info: {}".format(
            self.librarycounts.__dict__)
        )
        return self.librarycounts
