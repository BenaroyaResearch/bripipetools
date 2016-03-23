import os, glob

def locate_root_folder(folder_name, max_depth=3):
    for d in range(1, max_depth + 1):
        max_glob = ('/').join('*' * d)
        root_glob = os.path.join('/', max_glob)
        print root_glob
        for f in glob.glob(root_glob):
            if folder_name in f:
                return f
                break

class SystemFile(object):
    def __init__(self, file_path):

        self.path = file_path

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
