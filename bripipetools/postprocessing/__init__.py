"""
Covers a range of operations performed on outputs and other files
produced through bioinformatics processing of a batch of samples. For
example, the ``postprocess.stitching`` submodule parses data from
individual files of similar type and combines data into a single table
for all samples in a project. By extension, ``postprocess.mergin``
will take these stitched tables of different types and combine them
into a new, large table for the project. On the other hand, the
``postprocess.cleanup`` submodule deals with fixing the way files
are named and organized on the disk.
"""
from .stitching import OutputStitcher
from .cleanup import OutputCleaner
from .compiling import OutputCompiler
