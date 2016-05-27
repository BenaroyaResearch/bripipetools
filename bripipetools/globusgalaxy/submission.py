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

    def _add_workflow_project_association(self, workflow, project):
        """
        Create association between workflow and project.
        """
        workflow.setdefault('projects', []).append(project)
        return workflow

    def _format_project_choice(self, project, workflows):
        """
        Format project for selection prompt: only print project ID and
        indexes of currently associated workflows.
        """
        workflow_nums = [idx for idx, w in enumerate(workflows)
                         for p in w['projects']
                         if project['name'] == p['name']]
        return '{} {}'.format(project['name'], workflow_nums)

    def _select_project_prompt(self):
        """
        Display the command-line prompt for selecting an individual project.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Type the number of the project you wish to "
                             "select or hit enter to finish: ")

    def _select_project(self):
        """
        Select and store project (path to unaligned folder) from among list of
        projects found in flowcell folder.

        :rtype: list
        :return: A list with the name of the batch file corresponding to user
            command-line selection.
        """
        projects = self.projects
        workflows = self.workflows
        project_choices = [self._format_project_choice(p, workflows)
                           for p in projects]

        print("\nFound the following projects: [current workflows selected]")
        ui.list_options(project_choices)
        project_i = ui.input_to_int(self._select_project_prompt)

        if project_i is not None:
            return projects[project_i]

    def _select_workflow_prompt(self):
        """
        Display the command-line prompt for selecting an individual workflow.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Type the number of the workflow to use: ")

    def _select_workflow(self):
        """
        Select workflow for current project.

        :rtype: list
        :return: A list with the name of the batch file corresponding to user
            command-line selection.
        """
        workflows = self.workflows
        workflow_choices = [w['name'] for w in workflows]

        ui.list_options(workflow_choices)
        workflow_i = ui.input_to_int(self._select_workflow_prompt)
        return workflows[workflow_i]

    def _update_batch_workflows(self):
        """
        Add workflow-project_associations for selected projects in the current
        flowcell.
        """
        project = self._select_project()
        workflow = self._select_workflow()
        return project
        # while True:
        #     project = self._select_project()
        #     if project is not None:
        #         print("\nProject {} selected.\n".format(project['name']))
        #         workflow = self._select_workflow()
        #         # print("\nWorkflow {} selected.\n".format(workflow['name']))
        #         # self._add_workflow_project_association(workflow, project)
        #     else:
        #         break
