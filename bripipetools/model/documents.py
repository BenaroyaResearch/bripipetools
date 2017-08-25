"""
Classes representing documents in the GenLIMS database.
"""
import logging
import re
import datetime

from .. import util
from .. import parsing

logger = logging.getLogger(__name__)


def convert_keys(obj):
    """
    Convert keys in a dictionary (or nested dictionary) from snake_case
    to camelCase; ignore '_id' keys.

    :type obj: dict, list
    :param obj: A dict or list of dicts with string keys to be
        converted.
    :rtype: dict, list
    :return: A dict or list of dicts with string keys converted from
        snake_case to camelCase.
    """
    if isinstance(obj, list):
        return [convert_keys(i) for i in obj]
    elif isinstance(obj, dict):
        return {(util.to_camel_case(k.lstrip('_'))
                 if not re.search('^_id', k)
                 else k): convert_keys(obj[k])
                for k in obj}
    else:
        return obj


class TG3Object(object):
    """
    Generic functions for objects in TG3 collections.

    :type _id: str
    :param _id: unique object identifier in the GenLIMS/TG3 Mongo
        database

    :type type: str
    :param type: field indicating object type in a collection

    :type is_mapped: bool
    :param is_mapped: flag indicating whether class instance was
        mapped from a database object (True) or created from
        scratch (False)
    """
    def __init__(self, _id=None, type=None, is_mapped=False):
        self._id = _id
        self.type = type
        self.date_created = datetime.datetime.now()
        self.last_updated = self.date_created
        self.is_mapped = is_mapped

    def update_attrs(self, attr_map, force=False):
        """
        Given a dictionary of key-value pairs for attribute names with
        new values, update each attribute. Always update empty ('None')
        attributes and set any new attributes; update all modified
        attributes if force option is 'True'.

        :type attr_map: dict
        :param attr_map: a dict with key-value pairs representing
            object attributes and values to which they should be set

        :type force: bool
        :param force: force overwrite of object fields in database, if
            they already exist
        """
        updated = False
        for attr, val in attr_map.items():
            if hasattr(self, attr):
                if (getattr(self, attr) is None
                        or (getattr(self, attr) != val and force)):
                    logger.debug("setting attribute '{}' as '{}'"
                                 .format(attr, val))
                    setattr(self, attr, val)
                    updated = True
            else:
                setattr(self, attr, val)
                logger.debug("setting attribute '{}' as '{}'"
                             .format(attr, val))
                updated = True
        if updated and not self.is_mapped:
            self.last_updated = datetime.datetime.now()
        else:
            logger.debug("no attributes updated")

    def to_json(self):
        """
        Return object attributes as dictionary with keys formatted as
        camel case.

        :rtype: dict
        :return: a dict containing class instance attributes, with all
            field names converted from snake case to camel case
        """
        return convert_keys(self.__dict__)


class GenericSample(TG3Object):
    """
    GenLIMS object in the 'samples' collection

    :type project_id: int
    :param project_id: Genomics Core project number

    :type: subproject_id: int
    :param subproject_id: Genomics Core sub-project number

    :type protocol_id: str
    :param protocol_id: unique ID of a protocol object in the GenLIMS
        database (in the 'protocols' collection)

    :type parent_id: str
    :param parent_id: unique ID of a sample object in the GenLIMS
        database from which the current sample was derived (in the
        'samples' collection)
    """
    def __init__(self, project_id=None, subproject_id=None, protocol_id=None,
                 parent_id=None, **kwargs):
        self.project_id = project_id
        self.subproject_id = subproject_id
        self.protocol_id = protocol_id
        self.parent_id = parent_id
        super(GenericSample, self).__init__(**kwargs)


class Library(GenericSample):
    """
    GenLIMS object in 'samples' collection of type 'library'
    """
    def __init__(self, **kwargs):
        sample_type = 'library'
        super(Library, self).__init__(type=sample_type, **kwargs)


class SequencedLibrary(GenericSample):
    """
    GenLIMS object in 'samples' collection of type 'sequenced library'

    :type run_id: str
    :param run_id: unique ID of a run object in the GenLIMS database
    """
    def __init__(self, run_id=None, **kwargs):
        sample_type = 'sequenced library'
        self.run_id = run_id
        self._raw_data = []
        super(SequencedLibrary, self).__init__(type=sample_type, **kwargs)

    @property
    def raw_data(self):
        """
        Return list of dictionaries with information about each raw
        data file (i.e., FASTQ) for a sequenced library.
        """
        return self._raw_data

    @raw_data.setter
    def raw_data(self, value):
        """
        Set raw data.
        """
        self._raw_data = value


class ProcessedLibrary(GenericSample):
    """
    GenLIMS object in 'samples' collection of type 'processed library'
    """
    def __init__(self, **kwargs):
        sample_type = 'processed library'
        self._processed_data = []
        super(ProcessedLibrary, self).__init__(type=sample_type, **kwargs)

    @property
    def processed_data(self):
        """
        Return list of dictionaries with information about each set
        of data processing outputs (i.e., from workflow batches).
        """
        return self._processed_data

    @processed_data.setter
    def processed_data(self, value):
        """
        Set processed data.
        """
        self._processed_data = value

class GeneCounts(TG3Object):
    """
    Research Database object in 'counts' collection of type 'Library Counts'
    """
    def __init__(self, **kwargs):
        sample_type = 'gene counts'
        self._gene_counts = []
        super(GeneCounts, self).__init__(type=sample_type, **kwargs)

    @property
    def gene_counts(self):
        """
        Return list of dictionaries with information about each set
        of data processing outputs (i.e., from workflow batches).
        """
        return self._gene_counts

    @gene_counts.setter
    def gene_counts(self, value):
        """
        Set processed data.
        """
        self._gene_counts = value

class Metrics(TG3Object):
    """
    Research Database object in 'counts' collection of type 'Library Counts'
    """
    def __init__(self, **kwargs):
        sample_type = 'metrics'
        self._metrics = []
        super(Metrics, self).__init__(type=sample_type, **kwargs)

    @property
    def metrics(self):
        """
        Return list of dictionaries with information about each set
        of data processing outputs (i.e., from workflow batches).
        """
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        """
        Set processed data.
        """
        self._metrics = value


class GenericRun(TG3Object):
    """
    GenLIMS object in the 'runs' collection

    :type protocol_id: str
    :param protocol_id: unique ID of a protocol object in the GenLIMS
        database (in the 'protocols' collection)

    :type date: str
    :param date: string indicating date of the run in ISO 8601 format
    """
    def __init__(self, protocol_id=None, date=None, **kwargs):
        self.protocol_id = protocol_id
        self.date = date
        super(GenericRun, self).__init__(**kwargs)


class FlowcellRun(GenericRun):
    """
    GenLIMS object in the 'runs' collection of type 'flowcell'.
    """
    _flowcell_path = None

    def __init__(self, **kwargs):
        run_type = 'flowcell'
        run_id = kwargs.get('_id')
        run_items = parsing.parse_flowcell_run_id(run_id)
        self.instrument_id = run_items['instrument_id']
        self.run_number = run_items['run_number']
        self.flowcell_id = run_items['flowcell_id']
        self.flowcell_position = run_items['flowcell_position']
        super(FlowcellRun, self).__init__(type=run_type,
                                          date=run_items['date'], **kwargs)

    @property
    def flowcell_path(self):
        """
        Return root-agnostic path to flowcell data folder.
        """
        return self._flowcell_path

    @flowcell_path.setter
    def flowcell_path(self, value):
        """
        Set flowcell path.
        """
        self._flowcell_path = value


class GenericWorkflow(TG3Object):
    """
    GenLIMS object in the 'workflows' collection
    """
    def __init__(self, **kwargs):
        super(GenericWorkflow, self).__init__(**kwargs)


class GlobusGalaxyWorkflow(TG3Object):
    """
    GenLIMS object in 'workflows' collection of type 'Globus Galaxy
    workflow'
    """
    def __init__(self, **kwargs):
        workflow_type = 'Globus Galaxy workflow'
        super(GlobusGalaxyWorkflow, self).__init__(type=workflow_type,
                                                   **kwargs)


class GenericWorkflowBatch(TG3Object):
    """
    GenLIMS object in the 'workflow batches' collection
    """
    def __init__(self, **kwargs):
        super(GenericWorkflowBatch, self).__init__(**kwargs)


class GalaxyWorkflowBatch(TG3Object):
    """
    GenLIMS object in 'workflow batches' collection of type 'Galaxy
    workflow'

    :type workflowbatch_file: str
    :param workflowbatch_file: path to file describing samples and
        parameters of Globus Galaxy workflow batch
    """
    def __init__(self, workflowbatch_file=None, **kwargs):
        workflow_batch_type = 'Galaxy workflow batch'
        self.workflowbatch_file = workflowbatch_file
        super(GalaxyWorkflowBatch, self).__init__(type=workflow_batch_type,
                                                  **kwargs)
