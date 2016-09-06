import re

# wrapper function for regex matching
def matchdefault(pattern, string, default=''):
    """
    Search for pattern in string and return default string if no match.
    """
    regex = re.compile(pattern)
    match = regex.search(string)
    if match is not None:
        return match.group()
    else:
        return default

def to_camel_case(snake_str):
    """
    Convert snake_case string to camelCase.
    """
    if re.search('_', snake_str):
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    else:
        return snake_str

def to_snake_case(camel_str):
    """
    Convert camelCase to snake_case.
    found function here:
    http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
