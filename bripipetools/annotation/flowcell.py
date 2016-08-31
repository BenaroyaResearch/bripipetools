
class FlowcellRunAnnotator(object):
    """
    Identifies, stores, and updates information about a flowcell run.
    """
    def __init__(run_id):
        self.run_id = run_id
        self.flowcellrun = self._init_flowcellrun(run_id)

    def _init_flowcellrun(run_id):
        """
        Try to retrieve data for the flowcell run from GenLIMS; if
        unsuccessful, create new ``FlowcellRun`` object.
        """
        try:
            return genlims.get_run(_id=run_id)
        except:
            return model.FlowcellRun(_id=run_id)

    # def _get_flowcell_path(folder):
    #     """
    #     Find
    #     """
    #
    # def _get_unaligned_folder(self):
