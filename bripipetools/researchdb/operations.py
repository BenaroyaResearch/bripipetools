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
            logger.debug("searching '{}' collection with query '{}'"
                         .format(collection, query))
            return list(db[collection].find(query))
        return wrapper
    return decorator


def insert_objects(collection):
    """
    Return a decorator that inserts one or more objects in into
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
                logger.debug("inserting '{}' into '{}' collection"
                             .format(o, collection))
                for k, v in o.items():
                    if v is not None:
                        logger.debug("updating field {}".format(k))
                        db[collection].update_one({'_id': o['_id']},
                                                  {'$set': {k: v}},
                                                  upsert=True)

        return wrapper
    return decorator


@find_objects('counts')
def get_counts(db, query):
    """
    Return list of documents from 'counts' collection based on query.
    """
    return db, query


@insert_objects('counts')
def put_counts(db, counts):
    """
    Insert each document in list into 'counts' collection.
    """
    return db, counts

