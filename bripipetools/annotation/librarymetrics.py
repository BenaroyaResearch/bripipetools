"""
Get/Insert library metrics
"""
import logging
import os
import re

from .. import parsing
from .. import database
from .. import postprocessing
from .. import model as docs

logger = logging.getLogger(__name__)


class LibraryMetricsAnnotator(object):
    """
    Identifies, stores, and updates information about library gene counts.
    """
    def __init__(self, path, library, project, run_id, db):
        logger.debug("creating `LibraryMetricsAnnotator` instance "
                     "for path '{}' project '{}' library '{}'".format(path, project, library))
        self.path = path
        self.db = db
        self.library_id = parsing.get_library_id(library)
        self.run_id = run_id
        self.run_items = parsing.parse_flowcell_run_id(run_id)
        self.seqlib_id = '{}_{}'.format(self.library_id, self.run_items['flowcell_id'])
        self.librarymetrics = self._init_librarymetrics()

    def _init_librarymetrics(self):
        """
        Try to retrieve data for the sequenced library from ResearchDatabase;
        if unsuccessful, create new ``Metrics`` object.
        """
        logger.debug("initializing `Metrics` instance")
        try:
            logger.debug("getting `genomicsMetrics` from ResearchDatabase")
            return database.map_to_object(
                database.get_genomicsMetrics(self.db, {'_id': self.seqlib_id})[0])
        except IndexError:
            logger.debug("creating new `Metrics` object")
            return docs.Metrics(_id=self.seqlib_id)

    def _update_librarymetrics(self):
        """
        Add any missing fields to SequencedLibrary object.
        """
        logger.debug("updating `Metrics` object attributes")
        path = os.path.join(self.path, 'metrics')
        metrics = postprocessing.OutputReader(path).read_data(self.seqlib_id)
        #logger.info("library counts: {}".format(librarycounts))
#        logger.info("counts: {}".format(librarycounts))
#        project_items = parsing.parse_project_label(self.project_label)
#         update_fields = {'project_id': project_items['project_id'],
#                          'subproject_id': project_items['subproject_id'],
#                          'run_id': self.run_id,
#                          'parent_id': self.library_id}
        self.librarymetrics.is_mapped = False
        seqlib_id_parts = self.seqlib_id.split("_")
        self.librarymetrics.libraryId = seqlib_id_parts[0]
        self.librarymetrics.flowcellId = seqlib_id_parts[1]
        #self.librarymetrics.update_attrs(metrics, force=True)
        for m, r in metrics.items():
            #logger.info("{} metrics update_attrs {} <-> {}".format(self.seqlib_id, m, r))
            for v in r:
                #logger.info("{} metrics update_attrs {}".format(self.seqlib_id, v))
                self.librarymetrics.update_attrs(v, force=True)

    def get_library_metrics(self):
        """
        Return sequenced library object with updated fields.
        """
        self._update_librarymetrics()
        logger.debug("returning metrics object info: {}".format(
            self.librarymetrics.__dict__)
        )
        return self.librarymetrics
