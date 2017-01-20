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
    Given a list of sample paths or folders of sample paths as well
    as the path to a workflow tempate, creates a batch submit file
    for the input samples.

    :type paths: list
    :param paths: List of paths to sample folders, where each
        folder contains one or more lane-specifc FASTQ file
        (e.g., '<path-to-sample-folder>/sample_L001_R1.fastq.gz');
        list can alternatively include one or more paths to folders
        that contain sample folders (e.g., a project folder).
    :type workflow_template: str
    :param workflow_template: Path to workflow template file,
        exported from Globus Genomics for API batch submission.
    :type endpoint: str
    :param endpoint: Globus endpoint where input files are accessed
        and output files will be sent (e.g., 'jeddy#srvgridftp01').
    :type base_dir: str
    :param base_dir: Path to folder where outputs will be stored;
        outputs will be grouped into one or more
        'Project_<label>Processed' subfolder(s) in the ``base_dir``.
    :type submit_dir: str
    :param submit_dir: Name of folder where batch submit file will
        be saved. Folder will be created under ``base_dir``. Defaults
        to 'globus_batch_submission'.
    :type group_tag: str
    :param group_tag: String indicating overal group identifier for
        workflow batches (e.g., a flowcell ID).
    :type subgroup_tags: list
    :param subgroup_tags: List of strings indicating subgroup
        identifiers (e.g., project labels from a flowcell run).
    :type sort: bool
    :param sort: Flag indicating whether or not to sort samples from
        smallest to largest (based on total size of raw data files)
        before submitting; most useful when also restricting number
        of samples.
    :type num_samples: int
    :param num_samples: Number of samples to submit from each folder,
        if input paths are folders of sample folders.
    :type build: str
    :param build: ID string of reference genome build to be used
        for processing current set of samples.
    """
    def __init__(self, paths, workflow_template, endpoint, base_dir,
                 submit_dir=None, group_tag=None, subgroup_tags=None,
                 sort=False, num_samples=None, build='GRCh38'):
        logger.debug("creating `BatchCreator` instance")
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
            if not os.path.isdir(self.submit_dir):
                os.makedirs(self.submit_dir)

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
        """
        Construct unique batch name indicating date, workflow, and
        build, as well as any group or subgroup identifier tags.
        """
        workflow_id = os.path.splitext(
            os.path.basename(self.workflow_template)
        )[0]
        logger.debug("creating batch name from workflow ID '{}', "
                     "group tag '{}', subgroup tags {}, and date tag '{}'"
                     .format(workflow_id, self.group_tag, self.subgroup_tags,
                             self.date_tag))
        batch_inputs = '_'.join([self.group_tag,
                                 '_'.join(self.subgroup_tags)]).rstrip('_')
        return '{}_{}_{}_{}'.format(self.date_tag, batch_inputs, workflow_id,
                                    self.build)

    def _check_input_type(self):
        """
        Inspect list of input paths and determine whether they
        represent sample paths or folders of sample paths.
        """
        try:
            check_path = [os.path.join(self.paths[0], f)
                          for f in os.listdir(self.paths[0])
                          if not re.search('DS_Store', f)][0]
        except IndexError:
            logger.debug("input paths appear to be empty folders; exiting",
                         exc_info=True)
            raise
        logger.debug("checking whether input paths are sample folders "
                     "or folders of sample folders based on first path '{}' "
                     "and its first item '{}'"
                     .format(self.paths[0], check_path))

        if os.path.isdir(check_path):
            self.inputs_are_folders = True
        else:
            self.inputs_are_folders = False

    def _prep_target_dir(self, folder=None):
        """
        Create processed output folder for an invididual input folder
        or for the full set of samples.
        """
        if folder is not None:
            target_tag = parsing.get_project_label(os.path.basename(folder))
        else:
            target_tag = self.group_tag

        target_dir = os.path.join(
            self.base_dir,
            'Project_{}Processed_globus_{}'.format(target_tag, self.date_tag)
        )
        logger.debug("creating folder for processed outputs '{}'"
                     .format(target_dir))
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        return target_dir

    def _get_sample_paths(self, folder):
        """
        Return the list of sample paths for an invididual folder.
        Optionally, sort and subset sample paths.
        """
        sample_paths = [os.path.join(folder, s)
                        for s in os.listdir(folder)
                        if not re.search('DS_Store', s)]

        logger.debug("found the following sample paths: {}"
                     .format(sample_paths))

        if self.sort:
            logger.debug("sorting samples based on file size")
            sample_paths = sorted(
                sample_paths,
                key=lambda x: sum(os.path.getsize(os.path.join(x, f))
                                  for f in os.listdir(x))
            )
        else:
            sample_paths.sort()

        if self.num_samples is not None:
            max_samples = min(self.num_samples, len(sample_paths))
            logger.debug("subsetting paths for folder '{}' to {} samples"
                         .format(folder, max_samples))
            sample_paths = sample_paths[0:max_samples]

        return sample_paths

    def _get_input_params(self):
        """
        For each input folder or for the full list of sample paths,
        create and map values (e.g., file paths) to each parameter
        in the workflow template. Return the combined set of sample
        parameter values across all samples or folders.
        """
        self._check_input_type()
        if self.inputs_are_folders:
            batch_params = []
            for p in self.paths:
                logger.info("Setting parameters for samples in folder '{}'."
                            .format(p))
                target_dir = self._prep_target_dir(p)
                sample_paths = self._get_sample_paths(p)
                parameterizer = BatchParameterizer(
                    sample_paths=sample_paths,
                    parameters=self.workflow_data['parameters'],
                    endpoint=self.endpoint,
                    target_dir=target_dir,
                    build=self.build
                )
                parameterizer.parameterize()
                batch_params = batch_params + parameterizer.samples
        else:
            logger.info("Setting parameters for all samples.")
            target_dir = self._prep_target_dir()
            sample_paths = self.paths
            parameterizer = BatchParameterizer(
                sample_paths=sample_paths,
                parameters=self.workflow_data['parameters'],
                endpoint=self.endpoint,
                target_dir=target_dir,
                build=self.build
            )
            parameterizer.parameterize()
            batch_params = parameterizer.samples

        return batch_params

    def create_batch(self):
        """
        Create batch name, prepare output folders, parameterize
        samples, and write the workflow batch submit file.

        :rtype: str
        :return: Path to the batch submit file.
        """
        batch_name = self._build_batch_name()
        batch_filename = '{}.txt'.format(batch_name)
        batch_path = os.path.join(self.submit_dir, batch_filename)
        self.workflowbatch_file.data['samples'] = self._get_input_params()

        logger.debug("writing batch file with name '{}' to {}"
                     .format(batch_name,
                             os.path.join(self.submit_dir, batch_filename)))
        self.workflowbatch_file.write(
            os.path.join(self.submit_dir, batch_filename),
            batch_name=batch_name
        )
        return batch_path
