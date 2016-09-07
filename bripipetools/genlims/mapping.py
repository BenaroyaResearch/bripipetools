"""
Methods to map from Mongo documents to model classes.
"""
import logging
import re

from .. import util
from .. import model as docs

logger = logging.getLogger(__name__)

def map_keys(obj):
    """
    Convert keys in a dictionary (or nested dictionary) from camelCase
    to snake_case; ignore '_id' keys.

    :type obj: dict, list
    :param obj: A dict or list of dicts with string keys to be
        converted.
    :rtype: dict, list
    :return: A dict or list of dicts with string keys converted from
        camelCase to snake_case.
    """
    if isinstance(obj, list):
        return [map_keys(i) for i in obj]
    elif isinstance(obj, dict):
        return {(util.to_snake_case(k.lstrip('_'))
                 if not re.search('^_id', k)
             else k): map_keys(obj[k])
                for k in obj}
    else:
        return obj

def get_class(doc):
    """
    Find the matching class for the document, based on its type.
    """
    classes = [n for n in dir(docs)
               if re.search('^[A-Z]', n)]
    logger.debug("found the following classes: {}".format(classes))
    doc_type = re.sub(' ', '', doc['type'].title())
    logger.debug("searching for {}".format(doc_type))
    return [c for c in classes
            if c == doc_type][0]

def map_to_object(doc):
    """
    Convert document to model class of appropriate type.
    """
    doc_class = get_class(doc)
    MappedClass = getattr(docs, doc_class)
    logger.debug("mapping to instance of type {}".format(doc_class))
    obj = MappedClass(None)
    logger.debug("document has following fields: {}".format(doc.keys()))
    snake_doc = map_keys(doc)
    for k, v in snake_doc.items():
        logger.debug("setting attribute {} as {}".format(k, v))
        setattr(obj, k, v)
    return obj
