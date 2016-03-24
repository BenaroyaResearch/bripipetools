
import re
from bioblend import galaxy

class DatasetInspector(object):
    """
    Class with methods for collecting information about all downstream
    (output) Datasets for current input Dataset.
    """
    def __init__(self, galaxy_instance, dataset, history_id=None):

        self.gi = galaxy_instance
        self.dset = dataset
        self.hid = history_id

    def clean_dataset_name(self):
        """
        Format a Dataset name (to make it generic).
        """
        dataset_name = self.dset.get('name')
        dataset_name = re.sub("lib.*fastq", "input FASTQ", dataset_name)
        dataset_name = re.sub(" on data [0-9]+( and data [0-9]+)*", "",
                              dataset_name)
        dataset_name = re.sub("_.*(\:|\.)+", ": ", dataset_name)

        return dataset_name

    def get_dataset_inputs(self):

        get_provenance = self.gi.histories.show_dataset_provenance

        dataset_id = self.dset.get('id')

        dataset_params = (self.gi.histories
                          .show_dataset_provenance(self.hid, dataset_id)
                          .get('parameters'))

        dataset_inputs = [dataset_params[p].get(f) \
                          for p in dataset_params \
                          for f in dataset_params[p] \
                          if re.search('^id$', f)]

        return list(set(dataset_inputs))
