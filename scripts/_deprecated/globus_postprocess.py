import scripts._mypath
import sys, os, argparse, time, json, re
from bripipetools.globusgalaxy import postprocessing

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--flowcell_dir',
                        required=True,
                        default=None,
                        help=("specify the directory of unaligned library "
                              "FASTQs to be processed - e.g., "
                              "/mnt/genomics/Illumina/"
                              "150615_D00565_0087_AC6VG0ANXX/Unaligned"
                              "P43-12-23224208"))
    parser.add_argument('-c', '--check_only',
                        action='store_true',
                        help=("check that all outputs are present, but don't "
                              "attempt to compile"))
    parser.add_argument('-d', '--dry_run',
                        action='store_true',
                        help=("only report what would be done"))
    args = parser.parse_args()

    flowcell_dir = args.flowcell_dir
    check_only = args.check_only
    dry_run = args.dry_run

    out_manager = postprocessing.GlobusOutputManager(flowcell_dir)
    out_manager.check_batches()
    if not check_only:
        out_manager.curate_batches(dry_run=dry_run)


if __name__ == "__main__":
   main(sys.argv[1:])
