"""
Contains methods for interacting with - connecting to, retrieving data
from, and inserting data into - the GenLIMS database at a low level.
Under the hood, much of the functionality in this module relies on the
pymongo client library for MongoDB. The ``genlims.operations``
submodule provides wrapper functions for getting/putting objects
from/to commonly used database collections, while ``genlims.mapping``
helps to construct Python ``model`` class objects from database
objects. Methods in the ``genlims.connection`` module manage the
database connection, depending on environment and configurations.
"""
from .connection import connect
from .operations import (find_objects, insert_objects,
                         get_samples, get_runs, get_workflowbatches,
                         put_samples, put_runs, put_workflowbatches,
                         create_workflowbatch_id, search_ancestors)
from .mapping import (map_keys, get_model_class, map_to_object)
