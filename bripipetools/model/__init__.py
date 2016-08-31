
import re
import json

from bripipetools.util import strings

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
        return {(strings.to_camel_case(k) if not re.search('^_', k)
                 else k): convert_keys(obj[k])
                for k in obj}
    else:
        return obj


class TG3Object(object):
    """
    Generic functions for objects in TG3 collections.
    """
    def __init__(self, _id=None, type=None, date_created=None):

        self._id = _id
        self.type = type
        self.date_created = date_created

    def to_json(self):
        return convert_keys(self.__dict__)


class GenericSample(TG3Object):
    """
    GenLIMS object in the 'samples' collection
    """
    def __init__(self, project_id=None, subproject_id=None, protocol_id=None,
                 parent_id=None, **kwargs):
        self.project_id = project_id
        self.subproject_id = project_id
        self.protocol_id = protocol_id
        self.parent_id = parent_id
        super(GenericSample, self).__init__(**kwargs)

#
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
    """
    _raw_data = []

    def __init__(self, run_id=None, **kwargs):
        sample_type = 'sequenced library'
        self.run_id = run_id
        super(SequencedLibrary, self).__init__(type=sample_type, **kwargs)

    @property
    def raw_data(self):
        """
        Return list of dictionaries with information about each raw data
        file (i.e., FASTQ) for a sequenced library.
        """
        return self._raw_data

    @raw_data.setter
    def raw_data(self, value):
        """
        Set raw data.
        """
        self._raw_data = value
