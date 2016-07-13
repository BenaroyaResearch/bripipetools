#!/bin/python
import sys
import os
import shutil
import zipfile
import subprocess

def check_zip(path):
    zf = zipfile.ZipFile(path)
    return 'qcR1/' not in zf.namelist()

def unzip_qc(path):
    new_path = path.rstrip('.zip')
    args = ['unzip', '-d', new_path, path]
    subprocess.call(args)
    os.rename(path, path.replace('.zip', '_old.zip'))
    return new_path

def rezip_qc(path):
    shutil.make_archive(path, 'zip', base_dir='qcR1',
                        root_dir=os.path.dirname(path))
    shutil.rmtree(path)

def main(argv):
    qc_dir = os.path.abspath(sys.argv[1])
    for d in os.listdir(qc_dir):
        sample_dir = os.path.join(qc_dir, d)
        if os.path.isdir(sample_dir):
            print(d)
            qc_zip = os.path.join(sample_dir, 'qcR1.zip')
            if check_zip(qc_zip):
                print('Rezipping...')
                new_path = unzip_qc(qc_zip)
                rezip_qc(new_path)
            else:
                print('Skipping...')


if __name__ == "__main__":
   main(sys.argv[1:])
