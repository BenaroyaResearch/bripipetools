"""
Establishes the underlying data model linking data from bioinformatics
processing pipelines to the GenLIMS/TG3 database. Python class
representations of database objects (documents) are defined in the
``model.documents`` submodule. These classes include some basic
functionality, mostly related to setting/formatting attributes,
which are eventually fed back into the database as key-value pairs.
However, model classes are also the basic "currency" for several other
modules, where they are used to retrieve, modify, store, and return
data.

Depends on the ``util`` and ``parsing`` modules.
"""
from .documents import (convert_keys, TG3Object,
                        GenericSample, Library, SequencedLibrary,
                        ProcessedLibrary, GenericRun, FlowcellRun,
                        GenericWorkflow, GlobusGalaxyWorkflow,
                        GenericWorkflowBatch, GalaxyWorkflowBatch)
