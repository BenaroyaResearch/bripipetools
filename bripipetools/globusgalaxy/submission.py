"""
Create batch submission instructions for data processing jobs on Globus Galaxy.
"""

import os
import sys
import re

from bripipetools.util import ui

class GlobusSubmitManager(object):
    def __init__(self, flowcell_dir, workflow_dir, endpoint):
        """
        Prepares batch processing parameters (saved in a batch submit file) for
        one or more projects in an RNA-seq flowcell folder.

        :type flowcell_dir: str
        :param flowcell_dir: Path to flowcell folder where raw data (FASTQs) of
            projects to be processed in Globus Galaxy are stored.
        :type workflow_dir: str
        :param workflow_dir: Path to folder where empty/template batch submit
            files are stored for existing Globus Galaxy workflows.
        :endpoint: str
        :param endpoint: Globus endpoint where input data is stored and outputs
            are to be sent.
        """
        self.flowcell_dir = flowcell_dir
        self.unaligned_dir = os.path.join(flowcell_dir, 'Unaligned')
        self.workflow_dir = workflow_dir
        self.endpoint = endpoint
        self._set_projects()
        self._set_workflows()

    def _set_projects(self):
        """
        Identify projects & locate corresponding raw data folders in the
        'Unaligned' folder for the flowcell.
        """
        # TODO: should this be a property instead of setter method?
        unaligned_dir = self.unaligned_dir
        self.projects = [{'name': p,
                          'path': os.path.join(unaligned_dir, p)}
                         for p in os.listdir(unaligned_dir)
                         if '.' not in p]
        self.projects.sort()

    def _set_workflows(self):
        """
        Identify workflows in the workflow folder & store paths.
        """
        workflow_dir = self.workflow_dir
        self.workflows = [{'name': f,
                           'path': os.path.join(workflow_dir, f),
                           'projects': []}
                          for f in os.listdir(workflow_dir)
                          if 'Galaxy-API' not in f
                          and not re.search('^\.', f)]
        self.workflows.sort()

    def _format_project_choice(self, project, workflows):
        """
        Format project for selection prompt: only print project ID and
        indexes of currently associated workflows.
        """
        workflow_nums = [idx for idx, w in enumerate(workflows)
                         for p in w['projects']
                         if project['name'] == p['name']]
        return '{} {}'.format(project['name'], workflow_nums)

    def _select_workflow_prompt(self):
        """
        Display the command-line prompt for selecting an individual workflow.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Select workflow for which to create a batch: ")

    def _select_workflow(self):
        """
        Select workflow for current batch.

        :rtype: list
        :return: A list with the name of the batch file corresponding to user
            command-line selection.
        """
        workflows = self.workflows
        workflow_choices = [w['name'] for w in workflows]

        ui.list_options(workflow_choices)
        workflow_i = ui.input_to_int(self._select_workflow_prompt)

        if workflow_i is not None:
            return workflows[workflow_i]

    def _select_project_prompt(self):
        """
        Display the command-line prompt for selecting an individual project.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Type the number or numbers (separated by comma)"
                             " of project(s) you wish to add to the current"
                             " workflow batch, or hit enter to skip: ")

    def _select_projects(self):
        """
        Select and store project (path to unaligned folder) from among list of
        projects found in flowcell folder.

        :rtype: list
        :return: A list with the name of the batch file corresponding to user
            command-line selection.
        """
        projects = self.projects
        project_choices = [p['name'] for p in projects]

        print("\nFound the following projects:")
        ui.list_options(project_choices)
        project_i = ui.input_to_int_list(self._select_project_prompt)

        if project_i is not None:
            return [projects[i] for i in project_i]

    def _add_workflow_project_association(self, workflow, project):
        """
        Create association between workflow and project.
        """
        workflow.setdefault('projects', []).append(project)
        return workflow

    def _update_batch_workflows(self):
        """
        Add workflow-project_associations for selected projects in the current
        flowcell.
        """
        # project = self._select_project()
        # workflow = self._select_workflow()
        # return project
        workflows = self.workflows
        open_workflows = [w['name'] for w in workflows]
        while len(open_workflows) > 5:
            workflow = self._select_workflow()
            print("\nWorkflow {} selected.".format(workflow['name']))
            open_workflows.remove(workflow['name'])
            # sys.stderr.flush()

            projects = self._select_projects()
            workflow['projects'] = projects
            # print("\nWorkflow {} selected.\n".format(workflow['name']))
            # self._add_workflow_project_association(workflow, project)
