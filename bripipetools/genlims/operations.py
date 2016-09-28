"""
Basic operations for the GenLIMS Mongo database.
"""
import logging
logger = logging.getLogger(__name__)
import re
from functools import wraps

import pymongo

def find_objects(collection):
    """
    Return documents from specified collection based on query.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args):
            db, query = f(*args)
            logger.debug("searching {} collection with query {}"
                         .format(collection, query))
            return list(db[collection].find(query))
        return wrapper
    return decorator

def insert_objects(collection):
    """
    Insert each object in list into specified collection; if object exists,
    update any individual fields that are not empty in the input object.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args):
            db, objects = f(*args)
            objects = [objects] if not isinstance(objects, list) else objects
            logger.debug("inserting list of objects: {}".format(objects))
            for o in objects:
                logger.debug("inserting {} into {} collection"
                             .format(o, collection))
                for k, v in o.items():
                    if v is not None:
                        logger.debug("updating field {}".format(k))
                        db[collection].update_one({'_id': o['_id']},
                            {'$set': {k: v}}, upsert=True)

        return wrapper
    return decorator

@find_objects('samples')
def get_samples(db, query):
    """
    Return list of documents from 'samples' collection based on query.
    """
    return db, query

@find_objects('runs')
def get_runs(db, query):
    """
    Return list of documents from 'runs' collection based on query.
    """
    return db, query

@find_objects('workflowbatches')
def get_workflowbatches(db, query):
    """
    Return list of documents from 'workflow batches' collection based on query.
    """
    return db, query

@insert_objects('samples')
def put_samples(db, samples):
    """
    Insert each document in list into 'samples' collection.
    """
    return db, samples

@insert_objects('runs')
def put_runs(db, runs):
    """
    Insert each document in list into 'runs' collection.
    """
    return db, runs

@insert_objects('workflowbatches')
def put_workflowbatches(db, workflowbatches):
    """
    Insert each document in list into 'workflowbatches' collection.
    """
    return db, workflowbatches

def create_workflowbatch_id(db, prefix, date):
    """
    Check the 'workflowbatches' collection and construct ID with lowest
    available batch number (i.e., ''<prefix>_<date>_<number>').
    """
    query = {'_id': {'$regex': '{}_{}_.+'.format(prefix, date)}}
    logger.debug("searching 'workflowbatches' collection with query {}"
                 .format(query))
    workflowbatches = get_workflowbatches(db, query)
    num = 1

    if len(workflowbatches):
        while True:
            num_regex = re.compile('_{}$'.format(num))
            logger.debug("searching for workflowbatches {} ending in {}"
                         .format(workflowbatches, num))
            if any([num_regex.search(wb['_id']) for wb in workflowbatches]):
                num += 1
                break

    return '{}_{}_{}'.format(prefix, date, num)
