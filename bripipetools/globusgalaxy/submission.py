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

    def _format_workflow_choice(self, workflow):
        """
        Format workflow for selection prompt: only print workflow name and
        names of currently associated projects.

        :type workflow: dict
        :param workflow: A dict with name and path of workflow to be used for
            batch processing.

        :rtype: str
        :return: A string displaying the workflow name and the list of projects
            associated with the workflow for the current batch.
        """
        workflow_project_names = [p['name'] for p in workflow['projects']]
        return '{} [{}]'.format(workflow['name'],
                              ''.join(workflow_project_names))

    def _select_workflow_prompt(self):
        """
        Display the command-line prompt for selecting an individual workflow.

        :rtype: str
        :return: String collected from ``raw_input`` in response to the prompt.
        """
        return ui.prompt_raw("Select workflow for which to create a batch, or"
                             " hit enter to finish: ")

    def _select_workflow(self):
        """
        Select workflow for current batch.

        :rtype: dict
        :return: A dict with the name of the workflow and path to the template
            batch submit file corresponding to user command-line selection.
        """
        workflows = self.workflows
        workflow_choices = [self._format_workflow_choice(w)
                            for w in workflows]

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
        Select and store project from among list of projects found in flowcell
        folder.

        :rtype: list
        :return: A list of dicts with the name and path of each project folder,
            corresponding to user command-line selection.
        """
        projects = self.projects
        project_choices = [p['name'] for p in projects]

        print("\nFound the following projects:")
        ui.list_options(project_choices)
        project_i = ui.input_to_int_list(self._select_project_prompt)

        if project_i is not None:
            return [projects[i] for i in project_i]

    def _update_batch_workflows(self):
        """
        Interactively add workflow-project associations for projects in the
        current flowcell.
        """
        while True:
            workflow = self._select_workflow()
            if workflow is not None:
                print("\nWorkflow {} selected.".format(workflow['name']))
                projects = self._select_projects()
                workflow['projects'] = projects
            else:
                break
