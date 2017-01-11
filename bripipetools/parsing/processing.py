import logging
import datetime

from .. import util

logger = logging.getLogger(__name__)


def parse_batch_name(batch_name):
    """
    Parse batch name indicated in workflow batch submit file and
    return individual components indicating date, list of project
    labels, and flowcell ID.
    """
    name_parts = batch_name.split('_')
    date = datetime.datetime.strptime(name_parts.pop(0), '%y%m%d')

    fc_id = name_parts.pop(-1)

    return {'date': date, 'projects': name_parts, 'flowcell_id': fc_id}