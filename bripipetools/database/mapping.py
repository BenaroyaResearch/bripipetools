"""
bripipetools mapping submodule: methods to map from Mongo documents to model
classes.
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
    :param obj: a dict or list of dicts with string keys to be
        converted

    :rtype: dict, list
    :return: a dict or list of dicts with string keys converted from
        camelCase to snake_case
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


def get_model_class(doc):
    """
    Find the matching class for the document, based on its type.

    :type doc: dict
    :param doc: a dict representing a MongoDB document/object

    :rtype: str
    :return: a string representing the name of the matched class
        from the model module
    """
    classes = [n for n in dir(docs)
               if re.search('^[A-Z]', n)]
    logger.debug("found the following classes: {}".format(classes))
    doc_type = re.sub(' ', '', doc['type'].title())
    logger.debug("searching for '{}'".format(doc_type))
    return [c for c in classes
            if re.search(doc_type, c)][0]


def map_to_object(doc):
    """
    Convert document to model class of appropriate type.

    :type doc: dict
    :param doc: a dict representing a MongoDB document/object

    :rtype: type[docs.TG3Object]
    :return: an new instance of the matched model class
    """
    doc_class = get_model_class(doc)
    mappedclass = getattr(docs, doc_class)
    if (doc_class != 'GeneCounts'):
        logger.debug("mapping '{}' to instance of type '{}'"
                     .format(doc, doc_class))
    else:
        logger.debug("mapping instance of type '{}'"
                     .format(doc_class))
    obj = mappedclass(_id=doc['_id'], is_mapped=True)

    logger.debug("document has following fields: {}".format(list(doc.keys())))
    snake_doc = map_keys(doc)
    obj.update_attrs(snake_doc, force=True)
    return obj
