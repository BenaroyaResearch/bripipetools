import os
import glob
import re


def locate_root_folder(top_level, max_depth=3):
    """
    Find the root of a file path preceding a specified 'top level' directory.

    :type top_level: str
    :param top_level: Nominal 'top level' directory immediately following root
        (e.g., 'genomics' in '/Volumes/genomics'); should be a relatively
        unique folder name, at least within the specified depth).

    :type max_depth: str
    :param max_depth: How many directory levels down from the true system root
        to search for ``top_level`` folder.

    :rtype: str
    :return: A string representing the part of the file path starting from the
        current system root up to (but not including) the ``top_level`` folder.
    """
    for d in range(1, max_depth + 1):
        max_glob = '/'.join('*' * d)
        root_glob = os.path.join('/', max_glob)
        for f in glob.glob(root_glob):
            if top_level in f:
                return '{}/'.format(os.path.dirname(f))


def swap_root(path, top_level, new_root='/~/'):
    """
    Replace section of file path preceding a specified 'top level' directory
    with a different string (mostly for use with Globus transfers).

    :type path: str
    :param path: Any system file path.

    :type top_level: str
    :param top_level: Nominal 'top level' directory to immediately follow new
        root (e.g., 'genomics' in '/Volumes/genomics').

    :type new_root: str
    :param new_root: String specifying the new root of the file path.

    :rtype: str
    :return: modified path with new root
    """
    deroot_path = re.sub('.*(?={})'.format(top_level), '', path)
    return os.path.join(new_root, deroot_path)


