"""
Call ``flowcell_run`` QC submodule to collect and summarize statistics from an
Illumina flowcell sequencing run.
"""
import os
import sys

import _mypath
from bripipetools.qc import flowcell_run as fcqc

def main(argv):
    # only converts files for now
    flowcell_dir = sys.argv[1]
    fcqc.FlowcellRun(flowcell_dir).convert_barcode_data()
    
if __name__ == "__main__":
   main(sys.argv[1:])
