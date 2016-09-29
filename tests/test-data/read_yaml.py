import yaml
import os
from pprint import pprint

## define custom tag handler
def join(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

def ujoin(loader, node):
    seq = loader.construct_sequence(node)
    return '_'.join([str(i) for i in seq])


def join_path(d, root):
    """
    Walk down tree to recursively join paths.
    """
    for item in d:
        if isinstance(d[item], dict) and 'path' in d[item]:
            d[item]['path'] = os.path.join(root, d[item]['path'])
            d[item] = join_path(d[item], d[item]['path'])
    return d

## register the tag handler
yaml.add_constructor('!join', join)
yaml.add_constructor('!ujoin', ujoin)

with open('mock_genomics_server.yml', 'r') as stream:
    pprint(join_path(yaml.load(stream), './tests/test-data'))
