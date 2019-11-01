"""
Contains methods for interacting with - connecting to, retrieving data
from, and inserting data into - BRI databases (GenLIMS and ResDB) at 
a low level. Under the hood, much of the functionality in this package 
relies on the pymongo client library for MongoDB. The ``database.operations``
module provides wrapper functions for getting/putting objects
from/to commonly used database collections, while ``database.mapping``
helps to construct Python ``model`` class objects from database
documents. Methods in the ``database.connection`` module manage the
database connection, depending on environment and configurations.
"""
from .connection import connect
from .operations import (find_objects, insert_objects,
                         get_genomicsSamples, get_genomicsCounts, get_genomicsMetrics, get_genomicsRuns, get_genomicsWorkflowbatches,
                         put_genomicsSamples, put_genomicsCounts, put_genomicsMetrics, put_genomicsRuns, put_genomicsWorkflowbatches,
                         create_workflowbatch_id, search_ancestors)
from .mapping import (map_keys, get_model_class, map_to_object)