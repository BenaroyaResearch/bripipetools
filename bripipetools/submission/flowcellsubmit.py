import logging
import os
import re

from .. import parsing
from .. import annotation
from . import BatchCreator

logger = logging.getLogger(__name__)


class FlowcellSubmissionBuilder(object):
    """
    Prepares workflow batch submissions for all unaligned projects
    from a flowcell run.
    """
    def __init__(self, path, endpoint, db, workflow_dir=None,
                 all_workflows=True):
        logger.debug("creating `FlowcellSubmissionBuilder` instance "
                     "for path '{}'".format(path))
        self.path = path
        self.endpoint = endpoint
        self.db = db
        if workflow_dir is not None:
            self.workflow_dir = workflow_dir
        self.all_workflows = all_workflows
        self._init_annotator()

    def _init_annotator(self):
        logger.debug("initializing `FlowcellRunAnnotator` instance")
        path_items = parsing.parse_flowcell_path(self.path)
        self.annotator = annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            genomics_root=path_items['genomics_root'],
            db=self.db
        )

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

    def _get_project_paths(self):
        unaligned_path = self.annotator.get_unaligned_path()
        logger.debug("collecting unaligned projects in '{}'"
                     .format(unaligned_path))
        self.project_paths = [os.path.join(unaligned_path, p)
                              for p in self.annotator.get_projects()]
        logger.debug("found the following unaligned projects: {}"
                     .format([os.path.basename(os.path.normpath(f))
                              for f in self.project_paths]))

    def _assign_workflows(self):
        workflow_opts = self.get_workflow_options(
            optimized_only=not self.all_workflows
        )
        build_opts = ['GRCh38', 'NCBIM37', 'hg19', 'mm10', 'mm9']
        self._get_project_paths()

        continue_assign = True
        batch_map = {}
        while continue_assign:
            print("\nFound the following projects: "
                  "[current workflows selected]")
            for i, p in enumerate(self.project_paths):
                workflow_nums = [w for w, k in enumerate(workflow_opts)
                                 if p in batch_map.get(k, [])]
                print("   {} : {} {}".format(i, os.path.basename(p),
                                             str(workflow_nums)))

            p_i = raw_input("\nType the number of the project you wish "
                            "to select or hit enter to finish: ")

            if len(p_i):
                selected_project = self.project_paths[int(p_i)]

                for j, w in enumerate(workflow_opts):
                    print("   {} : {}".format(j, os.path.basename(w)))
                w_j = raw_input(("\nSelect the number of the workflow to use "
                                 "for project {}: ")
                                .format(os.path.basename(selected_project)))
                selected_workflow = workflow_opts[int(w_j)]

                for j, b in enumerate(build_opts):
                    print("   {} : {}".format(j, b))
                b_j = raw_input(("\nSelect the genome build to use "
                                 "for project {}: ")
                                .format(os.path.basename(selected_project)))
                selected_build = build_opts[int(b_j)]

                batch_key = (selected_workflow, selected_build)
                batch_map.setdefault(batch_key, []).append(
                    selected_project
                )
                logger.debug("current state of batch map: {}"
                             .format(batch_map))
            else:
                continue_assign = False
        self.batch_map = batch_map

    def _get_batch_tags(self, paths):
        group_tag = parsing.get_flowcell_id(self.path)
        subgroup_tags = [parsing.get_project_label(p) for p in paths]

        return group_tag, subgroup_tags

    def run(self, sort=False, num_samples=None):
        if not hasattr(self, 'batch_map'):
            self._assign_workflows()

        batch_paths = []
        for batchkey, projects in self.batch_map.items():
            workflow, build = batchkey
            logger.info("Building batch for workflow '{}' and build '{}' "
                        "with samples from projects: {}"
                        .format(os.path.basename(workflow), build, projects))
            group_tag, subgroup_tags = self._get_batch_tags(projects)
            creator = BatchCreator(
                paths=projects,
                workflow_template=workflow,
                endpoint=self.endpoint,
                base_dir=self.path,
                submit_dir='globus_batch_submission',
                group_tag=group_tag,
                subgroup_tags=subgroup_tags,
                sort=sort,
                num_samples=num_samples,
                build=build
            )
            batch_paths.append(creator.create_batch())
            logger.debug("workflow batch parameters saved in file '{}'"
                         .format(batch_paths[-1]))

        return batch_paths

