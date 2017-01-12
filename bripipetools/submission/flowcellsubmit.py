import os
import re

from .. import parsing
from .. import annotation


class FlowcellSubmissionBuilder(object):
    """

    """
    def __init__(self, path, endpoint, db, workflow_dir=None):
        self.path = path
        self.endpoint = endpoint
        self.db = db
        if workflow_dir is not None:
            self.workflow_dir = workflow_dir
        self._init_annotator()

    def _init_annotator(self):
        path_items = parsing.parse_flowcell_path(self.path)
        self.annotator = annotation.FlowcellRunAnnotator(
            run_id=path_items['run_id'],
            genomics_root=path_items['genomics_root'],
            db=self.db
        )

    def get_workflow_options(self, optimized_only=True):
        workflow_opts = [os.path.join(self.workflow_dir, f)
                         for f in os.listdir(self.workflow_dir)
                         if 'Galaxy-API' not in f]
        workflow_opts.sort()

        if optimized_only:
            workflow_opts = [f for f in workflow_opts
                             if re.search('optimized', f)]

        return workflow_opts

    def _get_project_paths(self):
        unaligned_path = self.annotator.get_unaligned_path()
        self.project_paths = [os.path.join(unaligned_path, p)
                              for p in self.annotator.get_projects()]

    def _assign_workflows(self):
        continue_assign = True
        batch_map = {}
        while continue_assign:
            print("\nFound the following projects: "
                  "[current workflows selected]")
            for i, p in enumerate(self.project_paths):
                workflow_nums = [w for w, k in enumerate(self.workflow_opts)
                                 if p in batch_map.get(k, [])]
                print("   {} : {} {}".format(i, os.path.basename(p),
                                             str(workflow_nums)))

            p_i = raw_input("\nType the number of the project you wish "
                            "to select or hit enter to finish: ")

            if len(p_i):
                selected_project = self.project_paths[int(p_i)]

                for j, w in enumerate(self.workflow_opts):
                    print("   {} : {}".format(j, os.path.basename(w)))
                w_j = raw_input(("\nSelect the number of the workflow to use "
                                 "for project {}: ")
                                .format(os.path.basename(selected_project)))
                selected_workflow = self.workflow_opts[int(w_j)]

                (batch_map.setdefault(selected_workflow, [])
                 .append(selected_project))
            else:
                continue_assign = False
        self.batch_map = batch_map

    # def build_lib_param_list(lib, endpoint, target_dir, header_keys, lane_order, fc_tag, build='GRCh38'):
    #     lib_params = []
    #     lib_id = parse_lib_path(lib)
    #     target_lib = lib_id + fc_tag
    #
    #     for param in header_keys:
    #         if 'SampleName' in param:
    #             lib_params.append(target_lib)
    #         elif 'fastq_in' in param:
    #             lib_params.append(endpoint)
    #             for lane in lane_order:
    #                 lib_params.append(get_lane_fastq(lib, lane))
    #         elif 'annotation' in param:
    #             ref_path = build_ref_path(param, build)
    #             lib_params.append(ref_path)
    #         elif 'out' in param:
    #             if re.search('^fastq_out', param):
    #                 final_fastq = '%s_R1-final.fastq.gz' % target_lib
    #                 result_path = os.path.join(format_endpoint_dir(target_dir),
    #                                           'inputFastqs', final_fastq)
    #             else:
    #                 result_path = build_result_path(target_lib, target_dir, param)
    #             lib_params.append(endpoint)
    #             lib_params.append(result_path)
    #
    #     return lib_params
