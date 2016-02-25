import os, glob

def find_dir(top_dir, dir_name, max_depth):
    for d in range(1, max_depth + 1):
        max_glob = "/".join("*" * d)
        top_glob = os.path.join(top_dir, max_glob)
        for f in glob.glob(top_glob):
            if dir_name in f:
                return f
                break

def get_file_type(file_path):
    ext = os.path.splitext(file_path)
    if 'z' in ext[-1]:
        compression = ext[-1].lstrip('.')
        ext = os.path.splitext(ext[0])[-1].lstrip('.')
    return ext, compression
