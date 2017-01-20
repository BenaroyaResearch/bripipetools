import logging
import os
import re

from . import BatchCreator

logger = logging.getLogger(__name__)


class SampleSubmissionBuilder(object):
    """
    Prepares workflow batch submissions for a list of sample paths
    or folders of sample paths.
    """
    def __init__(self, manifest, out_dir, endpoint, workflow_dir=None,
                 all_workflows=True, tag=None):
        logger.debug("creating `SampleSubmissionBuilder` instance")
        self.manifest = manifest

        self.out_dir = out_dir
        self.endpoint = endpoint
        if workflow_dir is not None:
            self.workflow_dir = workflow_dir
        self.all_workflows = all_workflows

        if tag is None:
            self.tag = ''
        else:
            self.tag = tag

    def _read_paths(self):
        with open(self.manifest) as f:
            self.paths = [p.rstrip() for p in f.readlines()]

    def get_workflow_options(self, optimized_only=True):
        logger.debug("collecting workflow templates from '{}'"
                     .format(self.workflow_dir))
        workflow_opts = [os.path.join(self.workflow_dir, f)
                         for f in os.listdir(self.workflow_dir)
                         if 'Galaxy-API' not in f
                         and not re.search('^\.', f)]
        workflow_opts.sort()
        logger.debug("found the following workflow options: {}"
                     .format([os.path.basename(f) for f in workflow_opts]))

        if optimized_only:
            workflow_opts = [f for f in workflow_opts
                             if re.search('optimized', f)]
            logger.debug("keeping only optimized workflows: {}"
                         .format([os.path.basename(f) for f in workflow_opts]))

        return workflow_opts

    def _assign_workflow(self):
        if not hasattr(self, 'paths'):
            self._read_paths()

        workflow_opts = self.get_workflow_options(
            optimized_only=not self.all_workflows
        )
        build_opts = ['GRCh38', 'NCBIM37', 'hg19', 'mm10', 'mm9']

        for j, w in enumerate(workflow_opts):
            print("   {} : {}".format(j, os.path.basename(w)))
        w_j = raw_input("\nSelect the number of the workflow to use: ")
        selected_workflow = workflow_opts[int(w_j)]

        for j, b in enumerate(build_opts):
            print("   {} : {}".format(j, b))
        b_j = raw_input("\nSelect the genome build to use: ")
        selected_build = build_opts[int(b_j)]

        batch_key = (selected_workflow, selected_build)
        batch_map = {batch_key: self.paths}
        logger.debug("current state of batch map: {}"
                     .format(batch_map))

        self.batch_map = batch_map

    def run(self):
        if not hasattr(self, 'batch_map'):
            self._assign_workflow()

        batch_paths = []
        for batchkey, paths in self.batch_map.items():
            workflow, build = batchkey
            logger.info("Building batch for workflow '{}' and build '{}'"
                        .format(os.path.basename(workflow), build))
            creator = BatchCreator(
                paths=paths,
                workflow_template=workflow,
                endpoint=self.endpoint,
                base_dir=self.out_dir,
                group_tag=self.tag,
                build=build
            )
            batch_paths.append(creator.create_batch())
            logger.debug("workflow batch parameters saved in file '{}'"
                         .format(batch_paths[-1]))

        return batch_paths
