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
        max_glob = ('/').join('*' * d)
        root_glob = os.path.join('/', max_glob)
        for f in glob.glob(root_glob):
            if top_level in f:
                return '{}/'.format(os.path.dirname(f))
                break

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
    """
    top_re = re.compile('.*(?={})'.format(top_level))
    return top_re.sub(new_root, path)

class SystemFile(object):
    def __init__(self, path):

        self.path = path

    def __repr__(self):

        return str(self.path)


    def get_file_ext(self):
        path = self.path
        # get all tokens following '.'
        ext_list = os.path.splitext(path)[1:]

        # combine and remove first '.'
        return ('').join(ext_list).lstrip('.')

    def get_file_compression(self, ext):
        ext_parts = os.path.splitext(ext)

        if 'z' in ext_parts[-1]:
            compression = ext_parts[-1].lstrip('.')
        else:
            # TODO: not sure why this is here...
            print path

        return compression

    def rename(self, new_path, dry_run=False):
        """
        Moves file to new path and updates object path.
        """
        original_file = self.path
        target_file = new_path

        if os.path.exists(target_file):
            print("   - Target file {} already exists".format(target_file))
            return 1
        elif not os.path.exists(original_file):
            print("   - Source file {} not found".format(original_file))
            return 1
        else:
            print("   - Moving {} to {}".format(original_file, target_file))
            if not dry_run:
                shutil.move(original_file, target_file)
                self.path = target_file
            return 0
