"""
Slightly more specialized than methods in the ``util.strings`` module,
provides functions for parsing and extracting information from strings
that follow some expected nomenclature. The primary examples of this
information are IDs, names, labels, and other metadata for files and
objects generated either by Illumina technology or the BRI Genomics
Core (via GenLIMS).

Depends on the ``util`` module.
"""
from .illumina import (get_project_label, parse_project_label,
                       get_library_id, get_flowcell_id, parse_flowcell_run_id,
                       parse_fastq_filename)
