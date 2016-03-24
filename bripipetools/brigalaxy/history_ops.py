from bripipetools.brigalaxy import dataset_ops
import networkx as nx

class HistoryInspector(object):
    """
    Class with methods for inspecting and performing operations with a Galaxy History.
    """
    def __init__(self, galaxy_instance, history_id=None):
        self.gi = galaxy_instance

        if not history_id:
            self.select_history()
        else:
            self.hid = history_id
            self.hname = (self.gi.histories.get_histories(self.hid)[0]
                          .get('name'))

    def select_history(self):
        """
        Select current Galaxy History.
        """
        # Get list of histories on Galaxy and print as user options
        history_list = self.gi.histories.get_histories()
        print "\nFound the following histories:"
        for t,h in enumerate(history_list):
            print "%3d : %s" % (t, h.get('name'))

        # For the selected history, get the ID and full history contents
        var = raw_input("Type the number of the History you wish to select: ")
        history = history_list[int(var)]
        self.hid = history.get('id')
        self.hname = history.get('name')

    def get_datasets(self):
        """
        Get list of all Datasets in History.
        """
        dataset_list = self.gi.histories.show_history(self.hid, contents=True)
        self.dlist = [d for d in dataset_list if not d.get('deleted')]

    def show_datasets(self):
        """
        View list of History Datasets.
        """
        if not hasattr(self, 'dlist'):
            self.get_datasets()

        return self.dlist

    def annotate_dataset_list(self):

        if not hasattr(self, 'dlist'):
            self.get_datasets()

        dataset_list = self.dlist
        dataset_dict = {}
        for d in dataset_list:
            di = dataset_ops.DatasetInspector(self.gi, d)

            dataset_dict[d.get('id')] = {'name': di.clean_dataset_name(),
                                         'num': d.get('hid')}

        self.ddict = dataset_dict

    def build_dataset_graph(self, dataset_graph={}):
        """
        Build graph representing input/output relationship of all Datasets in
        current History.
        """
        if not hasattr(self, 'dlist'):
            self.get_datasets()

        dataset_list = self.dlist
        # dataset_list = dataset_list[40:45]
        dataset_graph = nx.DiGraph()
        for d in dataset_list:
            di = dataset_ops.DatasetInspector(self.gi, d, self.hid)

            dataset_graph.add_edges_from([(i, d.get('id'))
                                          for i in di.get_dataset_inputs()])

        self.dset_graph = dataset_graph

    def show_dataset_graph(self):
        """
        View graph (dictionary) with input/output relationship for all
        Datasets in History.
        """
        if not hasattr(self, 'dg'):
            self.build_dataset_graph()

        return self.dset_graph
    #
    # def get_root_datasets(self):
    #     """
    #     Based on the Dataset graph, identify root Datasets in the History.
    #     """
    #     if not hasattr(self, 'dg'):
    #         self.build_dataset_graph()
    #
    #     output_dataset_list = [o for outputs in self.dg.values() \
    #                            for o in outputs]
    #     root_dataset_list = [d for d in self.dl \
    #                          if d.get('id') not in output_dataset_list]
    #     self.rdl = root_dataset_list
    #
    # def show_root_datasets(self):
    #     """
    #     Show list of root Datasets in current History.
    #     """
    #     if not hasattr(self, 'rdl'):
    #         get_root_datasets()
    #
    #     return self.rdl
    #
    # def get_input_datasets(self):
    #     """
    #     Get list of input (non-reference) Datasets for current History.
    #     """
    #     if not hasattr(self, 'rdl'):
    #         self.get_root_datasets()
    #
    #     input_dataset_list = [{d.get('id'): d.get('name')} \
    #         for d in self.rdl \
    #         if re.search('incoming',
    #         self.gi.datasets.show_dataset(d.get('id')).get('file_name'))]
    #
    #     self.idl = input_dataset_list
    #
    # def show_input_datasets(self):
    #     """
    #     View list of input (non-reference) Datasets for History.
    #     """
    #     if not hasattr(self, 'idl'):
    #         self.get_input_datasets()
    #
    #     return self.idl
    #
    # def collect_history_info(self):
    #     if not hasattr(self, 'idl'):
    #         self.get_input_datasets()
    #     if not hasattr(self, 'dd'):
    #         self.annotate_dataset_list()
