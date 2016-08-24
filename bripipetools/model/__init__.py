
class TG3Object(object):
    '''
    Generic functions for objects in TG3 collections.
    '''
    def __init__(self, _id=None, type=None):

        self._id = _id
        self.type = type

    # def to_db(self):
    #     return convert_keys(self.__dict__)


class GenericSample(TG3Object):
    '''
    GenLIMS object in the 'samples' collection
    '''
    def __init__(self, parent_id=None, **kwargs):
        self.parent_id = parent_id
        super(GenericSample, self).__init__(**kwargs)

#
class Library(GenericSample):
    '''
    GenLIMS object in 'samples' collection of type 'library'
    '''
    def __init__(self, **kwargs):
        sample_type = 'library'
        super(Library, self).__init__(type=sample_type, **kwargs)


class SequencedLibrary(GenericSample):
    '''
    GenLIMS object in 'samples' collection of type 'sequenced library'
    '''
    def __init__(self, **kwargs):
        sample_type = 'sequenced library'
        super(SequencedLibrary, self).__init__(type=sample_type, **kwargs)
