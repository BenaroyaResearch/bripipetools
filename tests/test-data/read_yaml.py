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
    if isinstance(d, dict):
        if 'path' in d:
            d['path'] = os.path.join(root, d['path'])
            root = d['path']
        for item in d:
            d[item] = join_path(d[item], root)

    elif isinstance(d, list):
        print("!!! d:: {}, ROOT:: {}".format(d, root))
        d = [join_path(item, root) for item in d]
        print("!!! NEW d:: {}, ROOT:: {}".format(d, root))

    return d

## register the tag handler
yaml.add_constructor('!join', join)
yaml.add_constructor('!ujoin', ujoin)

with open('mock_genomics_server.yml', 'r') as stream:
    pprint(join_path(yaml.load(stream), './tests/test-data'))
