import _mypath
import sys, os, argparse, time, json, re
from bripipetools.globusgalaxy import postprocessing

def read_batch_file(batch_file):
    with open(batch_file) as f:
        return f.readlines()

def locate_param_line(data):
    """
    Identify batch file header line with parameter names; return line
    number.
    """
    return [idx for idx, l in enumerate(data)
            if 'SampleName' in l][0]

def get_header_data(batch_file):
    batch_data = read_batch_file(batch_file)
    return batch_data[0:locate_param_line(batch_data)]

def get_rerun_params(batch_file, rerun_samples):
    batch_data = read_batch_file(batch_file)
    return [l for l in batch_data if l.split('\t')[0] in rerun_samples]

def write_rerun_batch_file(batch_file, header_data, rerun_params):
    rerun_batch_file = '{}_rerun.txt'.format(os.path.splitext(batch_file)[0])
    rerun_data = header_data + rerun_params
    with open(rerun_batch_file, 'w+') as f:
        f.writelines(rerun_data)
    return rerun_batch_file

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
    rerun_batch, rerun_samples = out_manager.check_batches()
    if rerun_samples:
        header_data = get_header_data(rerun_batch)
        rerun_params = get_rerun_params(rerun_batch, rerun_samples)
        rerun_batch_file = write_rerun_batch_file(rerun_batch, header_data,
                                                  rerun_params)
        print(rerun_batch_file)


if __name__ == "__main__":
   main(sys.argv[1:])
