import logging
import os
import yaml

import pytest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if os.environ.get('DB_PARAM_FILE') is None:
    os.environ['DB_PARAM_FILE'] = 'default.ini'


def join(loader, node):
    """
    Join YAML list items with no separator.
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])


def ujoin(loader, node):
    """
    Join YAML list items with '_' separator.
    """
    seq = loader.construct_sequence(node)
    return '_'.join([str(i) for i in seq])

yaml.add_constructor('!join', join)
yaml.add_constructor('!ujoin', ujoin)


def join_path(d, root):
    """
    Walk down tree to recursively join paths.
    """
    if isinstance(d, dict):
        if 'path' in d:
            d['path'] = os.path.join(root, d['path'])
            root = d['path']
        for item in d:
            d[item] = join_path(d[item], root)
    elif isinstance(d, list):
        d = [join_path(item, root) for item in d]
    return d


@pytest.fixture(scope='session')
def mock_genomics_server(request):
    logger.info(("[setup] mock 'genomics' server, connect "
                 "to mock 'genomics' server"))
    with open('./tests/test-data/mock_genomics_server.yml', 'r') as stream:
        data = join_path(yaml.load(stream), './tests/test-data')

    def fin():
        logger.info(("[teardown] mock 'genomics' server, disconnect "
                     "from mock 'genomics' server"))
    request.addfinalizer(fin)
    return data
