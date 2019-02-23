import re


def matchdefault(pattern, string, default=''):
    """
    Search for pattern in string and return default string if no match

    :type pattern: str
    :param pattern: non-compiled regular expression to search for in
        input string

    :type string: str
    :param string: any string

    :type default: str
    :param default: string to return if no match found

    :rtype: str
    :return: substring matched to regular expression or default string,
        if no match found
    """
    regex = re.compile(pattern)
    match = regex.search(string)
    if match is not None:
        return match.group()
    else:
        return default

def matchlastdefault(pattern, string, default=''):
    """
    Search for pattern in string *from right*, return default string if no match

    :type pattern: str
    :param pattern: non-compiled regular expression to search for in
        input string

    :type string: str
    :param string: any string

    :type default: str
    :param default: string to return if no match found

    :rtype: str
    :return: rightmost substring matched to regular expression 
        or default string, if no match found
    """
    regex = re.compile(pattern)
    matches = regex.findall(string)
    if len(matches):
        return matches[len(matches) - 1]
    else:
        return default


def to_camel_case(snake_str):
    """
    Convert snake_case string to camelCase

    :type snake_str: str
    :param snake_str: a string in snake_case format

    :rtype: str
    :return: input string converted to camelCase format
    """
    if re.search('_', snake_str):
        components = snake_str.split('_')
        return components[0].lower() + ''.join(x.title() for x in components[1:])
    else:
        return snake_str


def to_snake_case(camel_str):
    """
    Convert camelCase to snake_case.
    found function here:
    http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case

    :type camel_str: str
    :param camel_str: a string in camelCase format

    :rtype: str
    :return: input string converted to snake_case format
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
