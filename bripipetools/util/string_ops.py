import re

# wrapper function for regex matching
def matchdefault(pattern, string, default=''):

    regex = re.compile(pattern)
    match = regex.search(string)
    if match is not None:
        return match.group()
    else:
        return default

def to_camel_case(snake_str):
    if not re.search('^_', snake_str):
        components = snake_str.split('_')
        return components[0] + "".join(x.title() for x in components[1:])
    else:
        return snake_str
