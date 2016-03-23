import os, glob

def locate_root_folder(folder_name, max_depth):
    for d in range(1, max_depth + 1):
        max_glob = ('/').join('/' * d)
        root_glob = os.path.join('/', max_glob)
        for f in glob.glob(top_glob):
            if folder_name in f:
                return f
                break

class SystemFile(object):
    def __init__(self, file_path):

        self.path = file_path

    def __repr__(self):

        return str(self.path)


    def get_file_type(file_path):
        ext = os.path.splitext(file_path)
        if 'z' in ext[-1]:
            compression = ext[-1].lstrip('.')
            ext = os.path.splitext(ext[0])[-1].lstrip('.')
        else:
            print file_path

        return ext, compression
