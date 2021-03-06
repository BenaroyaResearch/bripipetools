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
            pipeline_root=path_items['pipeline_root'],
            db=self.db
        )

    def get_workflow_options(self, optimized_only=True):
        logger.debug("collecting workflow templates from '{}'"
                     .format(self.workflow_dir))
        workflow_opts = [os.path.join(self.workflow_dir, f)
                         for f in os.listdir(self.workflow_dir)
                         if 'Galaxy-API' not in f
                         and not re.search(r'^\.', f)
                         and re.search('.txt$', f)]
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
        self.project_paths.sort()
        logger.debug("found the following unaligned projects: {}"
                     .format([os.path.basename(os.path.normpath(f))
                              for f in self.project_paths]))

    def _assign_workflows(self):
        workflow_opts = self.get_workflow_options(
            optimized_only=not self.all_workflows
        )
        build_opts = ['GRCh38.77', 'GRCh38.91', 'NCBIM37.67', 'GRCm38.91', 'hg19', 'mm10', 'mm9', 'ebv']
        self._get_project_paths()

        continue_assign = True
        batch_map = {}
        while continue_assign:
            print("\nFound the following projects: "
                  "[current workflows (w) and builds (b) selected]")
            for i, p in enumerate(self.project_paths):
                opts_p = [x[0] for x in [x for x in list(batch_map.items()) if p in x[1]]]

                w_p = ['w:{}'.format([w for w, k in enumerate(workflow_opts)
                                      if k == opt[0]][0])
                       for opt in opts_p]
                b_p = ['b:{}'.format(opt[1]) for opt in opts_p]
                s_p = ['stranded' if opt[2] else 'unstranded'
                       for opt in opts_p]

                print(("   {} : {} {}".format(i, os.path.basename(p),
                                             list(zip(w_p, b_p, s_p)))))

            p_i = input("\nType the number of the project you wish "
                            "to select or hit enter to finish: ")

            if len(p_i):
                selected_project = self.project_paths[int(p_i)]

                for j, w in enumerate(workflow_opts):
                    print(("   {} : {}".format(j, os.path.basename(w))))
                w_j = input(("\nSelect the number of the workflow to use "
                                 "for project {}: ")
                                .format(os.path.basename(selected_project)))
                selected_workflow = workflow_opts[int(w_j)]

                for j, b in enumerate(build_opts):
                    print(("   {} : {}".format(j, b)))
                b_j = input(("\nSelect the genome build (and release, "
                                 "if applicable) to use for project {}: ")
                                .format(os.path.basename(selected_project)))
                selected_build = build_opts[int(b_j)]

                s_j = input("\nIs the library type stranded? (y/[n]): ")
                stranded = s_j == 'y'

                batch_key = (selected_workflow, selected_build, stranded)
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
        for batchkey, projects in list(self.batch_map.items()):
            workflow, build, stranded = batchkey
            
            # Need to handle new version of BaseSpace directory structure,
            # Old dir structure:
            # Project Folder -> Lib Folder -> fastq.gz file(s)
            # New dir structure:
            # Project Folder -> FASTQ Folder -> Lib Folder -> fastq.gz file(s)
            for i in range(0, len(projects)):
                # If new structure, there should only be one FASTQ folder.
                # IF old structure, first folder should contain a libID
                subdir = [s for s in os.listdir(projects[i])
                          if not re.search('DS_Store', s)][0]
                          
                logger.debug("Subdirectory of {} identified as {}"
                             .format(projects[i], subdir))
                             
                if (not re.search('lib[0-9]+', subdir) and 
                    not re.search('DS_Store', subdir)):
                    logger.debug("New BaseSpace dir type. Moving from {} to {}"
                                 .format(projects[i], subdir))
                    projects[i] = os.path.join(projects[i], subdir)
            
            
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
                build=build,
                stranded=stranded
            )
            batch_paths.append(creator.create_batch())
            logger.debug("workflow batch parameters saved in file '{}'"
                         .format(batch_paths[-1]))

        return batch_paths

