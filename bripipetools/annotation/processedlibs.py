"""

"""
import logging
import re

from .. import util
from .. import genlims
from .. import model as docs

logger = logging.getLogger(__name__)


class ProcessedLibraryAnnotator(object):
    """
    Identifies, stores, and updates information about a processed library.
    """
    def __init__(self, workflowbatch_id, params, db):
        logger.debug("creating an instance of ProcessedLibraryAnnotator")
        self.workflowbatch_id = workflowbatch_id
        logger.debug("workflowbatch_id set to {}".format(workflowbatch_id))
        self.db = db
        self.params = params
        self.seqlib_id = self._get_seqlib_id()
        self.proclib_id = '{}_processed'.format(self.seqlib_id)
        self.processedlibrary = self._init_processedlibrary()

    def _get_seqlib_id(self):
        """
        Return the ID of the parent sequenced library.
        """
        return [p['value'] for p in self.params
                if p['name'] == 'SampleName'][0]

    def _init_processedlibrary(self):
        """
        Try to retrieve data for the processed library from GenLIMS;
        if unsuccessful, create new ``ProcessedLibrary`` object.
        """
        logger.debug("initializing ProcessedLibrary instance")

        try:
            logger.debug("getting ProcessedLibrary from GenLIMS")
            return genlims.map_to_object(
                genlims.get_samples(self.db, {'_id': self.proclib_id})[0])
        except IndexError:
            logger.debug("creating new ProcessedLibrary object")
            return docs.ProcessedLibrary(_id=self.proclib_id)

    def _get_outputs(self):
        """
        Return the list of outputs from the processing workflow batch.
        """
        return {p['tag']: p['value'] for p in self.params
                if p['type'] == 'output' and p['name'] == 'to_path'}

    def _parse_output_name(self, output_name):
        """
        Parse output name indicated by parameter tag in workflow batch
        submit file and return individual components indicating name,
        source, and type.
        """
        name = re.sub('_out', '', output_name)
        name_parts = name.split('_')
        file_format = name_parts.pop(-1)
        output_type = name_parts.pop(-1)
        source = '_'.join(name_parts)

        return {'name': name, 'type': output_type, 'source': source}

    def _group_outputs(self):
        """
        Organize outputs according to type and source.
        """
        outputs = self._get_outputs()
        grouped_outputs = {}
        for k, v in outputs.items():
            if 'fastq_' not in k:
                output_items = self._parse_output_name(k)
                grouped_outputs.setdefault(
                    output_items['type'], []
                    ).append(
                        {'source': output_items['source'],
                         'file': util.swap_root(v, 'genomics', '/'),
                         'name': output_items['name']})
        return grouped_outputs

    def _append_processed_data(self):
        """
        Add details and outputs for current workflow batch to processed
        data array field for processed library.
        """
        processed_data = self.processedlibrary.processed_data
        if (not len(processed_data)
                or not any(d['workflowbatch_id'] == self.workflowbatch_id
                           for d in processed_data)):
            logger.debug("inserting outputs from new workflow batch {} "
                         "for processed library {}"
                         .format(self.workflowbatch_id, self.proclib_id))
            self.processedlibrary.processed_data.append(
                {'workflowbatch_id': self.workflowbatch_id,
                 'outputs': self._group_outputs()})
        else:
            logger.debug("updating outputs from workflow batch {} "
                         "for processed library {}"
                         .format(self.workflowbatch_id, self.proclib_id))
            batch_data = [d for d in processed_data
                          if d['workflowbatch_id'] == self.workflowbatch_id][0]
            batch_data['outputs'] = self._group_outputs()

    def _update_processedlibrary(self):
        """
        Add or update any missing fields in ProcessedLibrary object.
        """
        self._append_processed_data()

        update_fields = {'parent_id': self.seqlib_id}
        self.processedlibrary.is_mapped = False
        self.processedlibrary.update_attrs(update_fields, force=True)

    def get_processed_library(self):
        """
        Return updated ProcessedLibrary object.
        """
        self._update_processedlibrary()
        return self.processedlibrary