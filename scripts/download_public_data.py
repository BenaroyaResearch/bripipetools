import _mypath
from bripipetools.public_data import ncbi
import sys, os

def main(argv):
    accession = sys.argv[1]
    target_dir = sys.argv[2]

    ncbi.download_gse_data(accession, target_dir)

if __name__ == "__main__":
   main(sys.argv[1:])
