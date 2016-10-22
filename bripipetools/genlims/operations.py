"""
Basic operations for the GenLIMS Mongo database.
"""
import logging
import re
from functools import wraps
import datetime

from .. import util

logger = logging.getLogger(__name__)


def find_objects(collection):
    """
    Return a decorator that retrieves objects from the specified
    collection, given a db connection and query.

    :type collection: str
    :param collection: sString indicating the name of the collection
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
    Return a decorator that inserts one or more objectsin into
    specified collection; if object exists, updates any individual
    fields that are not empty in the input object.

    :type collection: str
    :param collection: string indicating the name of the collection
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
                                                  {'$set': {k: v}},
                                                  upsert=True)

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
    Return list of documents from 'workflow batches' collection based
    on query.
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

    :type db: type[pymongo.database.Database]
    :param db: database object for current MongoDB connection

    :type prefix: str
    :param prefix: base string for workflow batch ID, based on workflow
        batch type (e.g., 'globusgalaxy' for Globus Galaxy workflow

    :type date: type[datetime.datetime]
    :param date: date on which workflow batch was run

    :rtype: str
    :return: a unique ID for the workflow batch, with the prefix and
        date combination appended with the highest available integer
    """
    isodate = datetime.date.isoformat(date)
    query = {'_id': {'$regex': '{}_{}_.+'.format(prefix, isodate)}}
    logger.debug("searching 'workflowbatches' collection with query {}"
                 .format(query))
    workflowbatches = get_workflowbatches(db, query)
    logger.debug("matched workflow batches: {}".format(workflowbatches))

    num = 1
    if len(workflowbatches):
        num = max([int(util.matchdefault('\d$', wb['_id']))
                   for wb in workflowbatches])
        while True:
            num_regex = re.compile('_{}$'.format(num))
            logger.debug("searching for workflowbatches {} ending in {}"
                         .format(workflowbatches, num))
            if any([num_regex.search(wb['_id']) for wb in workflowbatches]):
                num += 1
                break

    return '{}_{}_{}'.format(prefix, isodate, num)


def search_ancestors(db, sample_id, field):
    """
    Given an object in the 'samples' collection, specified by the input
    ID, iteratively walk through ancestors based on 'parentId' until
    a value is found for the requested field.

    :type db: type[pymongo.database.Database]
    :param db: database object for current MongoDB connection

    :type sample_id: str
    :param sample_id: a unique ID for a sample in GenLIMS

    :type field: str
    :param field: the field for which to search among ancestor samples

    :return: value for field, if found
    """
    sample = db.samples.find_one({'_id': sample_id})
    if sample is not None:
        if field in sample:
            return sample[field]
        else:
            try:
                return search_ancestors(db, sample['parentId'], field)
            except KeyError:
                logger.debug("input sample '{}' has no mapped parent sample"
                             .format(sample_id),
                             exc_info=True)
    else:
        logger.debug("input sample '{}' not found in db"
                     .format(sample_id))
