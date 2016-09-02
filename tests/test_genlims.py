import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pytest
import os
import re

from bripipetools.genlims import GenLIMS

def test_genlims_connection():
    genlims_instance = GenLIMS('tg3')
    assert('samples' in genlims_instance.db.collection_names())
