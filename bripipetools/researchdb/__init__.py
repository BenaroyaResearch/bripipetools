"""
Contains methods for interacting with - connecting to, retrieving data
from, and inserting data into - the Research database at a low level.
Under the hood, much of the functionality in this package relies on
the pymongo client library for MongoDB. The ``researchdb.operations``
module provides wrapper functions for getting/putting objects
from/to commonly used database collections, while ``researchdb.mapping``
helps to construct Python ``model`` class objects from database
documents. Methods in the ``genlims.connection`` module manage the
database connection, depending on environment and configurations.
"""
from .connection import connect
from .operations import (find_objects, insert_objects,
                         get_counts,
                         put_counts)
from .mapping import (map_keys, get_model_class, map_to_object)
