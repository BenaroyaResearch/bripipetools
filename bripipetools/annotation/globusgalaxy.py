"""
Classify / provide details for objects generated from a Globus
Galaxy workflow processing batch performed by the BRI Bioinformatics
Core.
"""

import logging
logger = logging.getLogger(__name__)

import os
import re
import datetime
from bripipetools import io
from bripipetools import genlims
from bripipetools.genlims import mapping as odm
from bripipetools.model import documents as docs
from bripipetools.util import files
from bripipetools.parsing import illumina

class WorkflowBatchAnnotator(object):
    """
    Identifies, stores, and updates information about a workflow batch.
    """
    def __init__(self, workflowbatch_file, db, genomics_root):
        logger.info("creating an instance of WorkflowBatchAnnotator")
        self.workflowbatch_file = workflowbatch_file
        self.db = db

        self.workflowbatch_data = io.WorkflowBatchFile(
            self.workflowbatch_file,
            state='submit'
            ).parse()
        self.workflowbatch = self._init_workflowbatch()

        logger.debug("setting 'genomics' path")
        self.genomics_path = os.path.join(genomics_root, 'genomics')

    def _parse_batch_name(self, batch_name):
        """
        Parse batch name indicated in workflow batch submit file and
        return individual components indicating date, list of project
        labels, and flowcell ID.
        """
        name_parts = batch_name.split('_')
        d = datetime.datetime.strptime(name_parts.pop(0), '%y%m%d')
        date = datetime.date.isoformat(d)

        fc_id = name_parts.pop(-1)

        return {'date': date, 'projects': name_parts, 'flowcell_id': fc_id}

    def _init_workflowbatch(self):
        """
        Try to retrieve data for the workflow batch from GenLIMS; if
        unsuccessful, create new ``GalaxyWorkflowBatch`` object.
        """
        logger.info("initializing GalaxyWorkflowBatch instance")
        workflowbatch_file = files.swap_root(self.workflowbatch_file,
                                            'genomics', '/')
        try:
            logger.debug("getting GalaxyWorkflowBatch from GenLIMS; "
                         "searching for record with batch file {}"
                         .format(workflowbatch_file))
            return odm.map_to_object(
                genlims.get_workflowbatches(self.db,
                    {'workflowbatchFile': workflowbatch_file}
                    )[0]
                )
        except IndexError:
            logger.debug("creating new GalaxyWorkflowBatch object",
                         exc_info=True)

            batch_items = self._parse_batch_name(
                self.workflowbatch_data['batch_name']
            )

            workflowbatch_id = genlims.create_workflowbatch_id(
                db = self.db,
                prefix = 'globusgalaxy',
                date = batch_items['date']
            )
            return docs.GalaxyWorkflowBatch(
                _id=workflowbatch_id,
                workflowbatch_file=workflowbatch_file
            )

    def _update_workflowbatch(self):
        """
        Add any missing fields to GalaxyWorkflowBatch object.
        """
        logger.debug("updating GalaxyWorkflowBatch object attributes")

        batch_items = self._parse_batch_name(
            self.workflowbatch_data['batch_name']
        )

        self.workflowbatch.workflow_id = self.workflowbatch_data['workflow_name']
        self.workflowbatch.date = batch_items['date']
        self.workflowbatch.projects = batch_items['projects']
        self.workflowbatch.flowcell_id = batch_items['flowcell_id']

    def get_workflow_batch(self):
        """
        Return workflow batch object with updated fields.
        """

        self._update_workflowbatch()
        logger.debug("returning workflow batch object: {}".format(
            self.workflowbatch.to_json()
        ))
        return self.workflowbatch

    def get_sequenced_libraries(self):
        """
        Collect list of sequenced libraries processed as part of
        workflow batch.
        """
        return [p['value']
                for s in self.workflowbatch_data['samples']
                for p in s
                if p['name'] == 'SampleName']

    # def get_sequenced_libraries(self, project=None):
    #     """
    #     Collect sequenced library objects for flowcell run.
    #     """
    #     unaligned_path = self._get_unaligned_path()
    #     projects = self.get_projects()
    #     if project is not None:
    #         logger.debug("subsetting projects")
    #         projects = [p for p in projects
    #                     if re.search(project, p)]
    #     for p in projects:
    #         logger.info("getting sequenced libraries for project {}".format(p))
    #         libraries = self.get_libraries(p)
    #         return [SequencedLibraryAnnotator(
    #                     os.path.join(unaligned_path, p, l),
    #                     l, p, self.run_id
    #                 ).get_sequenced_library() for l in libraries]

class ProcessedLibraryAnnotator(object):
    """
    Identifies, stores, and updates information about a processed library.
    """
    def __init__(self, workflowbatch_id, params, db):
        logger.info("creating an instance of ProcessedLibraryAnnotator")
        self.workflowbatch_id = workflowbatch_id
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
        logger.info("initializing ProcessedLibrary instance")
        try:
            logger.debug("getting ProcessedLibrary from GenLIMS")
            return odm.map_to_object(
                genlims.get_samples(self.db, {'_id': self.proclib_id})[0]
                )
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
        name = output_name.rstrip('_out')
        name_parts = name.split('_')
        file_format = name_parts.pop(-1)
        output_type = name_parts.pop(-1)
        source = ('_').join(name_parts)

        return {'name': name, 'type': output_type, 'source': source}

    def _group_outputs(self):
        """
        Organize outputs according to type and source.
        """
        outputs = self._get_outputs()
        logger.debug("grouping outputs: {}".format(outputs))
        grouped_outputs = {}
        for k, v in outputs.items():
            if 'fastq' not in k:
                output_items = self._parse_output_name(k)
                grouped_outputs.setdefault(
                    output_items['type'],
                    []
                ).append(
                    {'source': output_items['source'],
                     'file': files.swap_root(v, 'genomics', '/'),
                     'name': output_items['name']}
                )
        logger.debug("grouped outputs: {}".format(grouped_outputs))
        return grouped_outputs
