import logging
import os
import re
import datetime

from .. import parsing
from .. import io
from . import BatchParameterizer

logger = logging.getLogger(__name__)


class BatchCreator(object):
    """

    """
    def __init__(self, paths, workflow_template, endpoint, base_dir,
                 submit_dir=None, group_tag=None, subgroup_tags=None,
                 sort=False, num_samples=None, build='GRCh38'):
        self.paths = paths
        self.workflow_template = workflow_template
        self.workflowbatch_file = io.WorkflowBatchFile(
            path=self.workflow_template,
            state='template'
        )
        self.workflow_data = self.workflowbatch_file.parse()

        self.endpoint = endpoint
        self.base_dir = base_dir
        if submit_dir is None:
            self.submit_dir = base_dir
        else:
            self.submit_dir = os.path.join(base_dir, submit_dir)

        if group_tag is None:
            self.group_tag = ''
        else:
            self.group_tag = group_tag

        if subgroup_tags is None:
            self.subgroup_tags = ['']
        else:
            self.subgroup_tags = subgroup_tags
        self.date_tag = datetime.date.today().strftime("%y%m%d")

        self.build = build
        self.sort = sort
        self.num_samples = num_samples

    def _build_batch_name(self):
        workflow_id = os.path.splitext(
            os.path.basename(self.workflow_template)
        )[0]
        batch_inputs = '_'.join([self.group_tag,
                                 '_'.join(self.subgroup_tags)]).rstrip('_')
        return '{}_{}_{}'.format(self.date_tag, batch_inputs, workflow_id)

    def _get_sample_paths(self, path):
        sample_paths = [os.path.join(path, s)
                        for s in os.listdir(path)]

        if self.sort:
            sample_paths = sorted(
                sample_paths,
                key=lambda x: sum(os.path.getsize(os.path.join(x, f))
                                  for f in os.listdir(x))
            )

        if self.num_samples is not None:
            sample_paths = sample_paths[0:self.num_samples]

        return sample_paths

    def _prep_target_dir(self):
        pass

    def _get_input_params(self):
        if os.path.isdir(self.paths[0]):
            batch_params = []
            for p in self.paths:
                target_dir = self._prep_target_dir(p)
                sample_paths = self._get_sample_paths(p)
                parameterizer = BatchParameterizer(
                    sample_paths=sample_paths,
                    parameters=self.workflow_data['parameters'],
                    endpoint=self.endpoint,
                    target_dir=target_dir
                ).parameterize()
                batch_params = batch_params + parameterizer.samples
        else:
            target_dir = self._prep_target_dir()
            sample_paths = self.paths
            parameterizer = BatchParameterizer(
                sample_paths=sample_paths,
                parameters=self.workflow_data['parameters'],
                endpoint=self.endpoint,
                target_dir=target_dir
            ).parameterize()
            batch_params = parameterizer.samples

        return batch_params

    def create_batch(self):
        batch_name = self._build_batch_name()
        batch_filename = '{}.txt'.format(batch_name)
        self.workflowbatch_file.data['batch_name'] = batch_name
        self.workflowbatch_file.data['samples'] = self._get_input_params()
        self.workflowbatch_file.write(
            os.path.join(self.submit_dir, '{}.txt'.format(batch_filename))
        )






    # def get_project_params(endpoint, header_keys, lane_order, unaligned_dir,
    #                        project_lines=None, N=None, sort=False, build='GRCh38'):
    #     if project_lines is None:
    #         project_lines = []
    #
    #     fc_tag, proj = parse_unaligned_path(unaligned_dir)
    #
    #     sample_paths = [os.path.join(unaligned_dir, entry)
    #                     for entry in os.listdir(unaligned_dir)
    #                     if os.path.isdir(os.path.join(unaligned_dir, entry))]
    #
    #     if sort:
    #         sample_paths = sorted(sample_paths,
    #                               key=lambda x: sum(os.path.getsize(os.path.join(x, f))
    #                                                 for f in os.listdir(x)))
    #
    #     if N is not None:
    #         sample_paths = sample_paths[0:N]  # first N libs, any project
    #
    #     # target_dir, date_tag = prep_output_directory(unaligned_dir, proj)
    #
    #     for lib in unaligned_libs:
    #         if "Undetermined" not in lib:
    #             lib_params = build_lib_param_list(lib, endpoint, target_dir,
    #                                               header_keys, lane_order, fc_tag,
    #                                               build)
    #             project_lines.append(('\t').join(lib_params) + '\n')
    #
    #     return (proj, fc_tag, project_lines, date_tag)