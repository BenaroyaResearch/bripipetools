"""
Contains classes and methods for performing post-hoc quality control
operations on raw or processed genomics data. Submodules are organized
according to the specifc QC step performed. Unlike routine quality
inspection metrics and information provided by standard bioinformatics
tools through processing workflows, submodules here are aimed more at
identifying problems with sample handling or data generation. As such,
outputs from these submodules are designated as a special type,
'validation', to distinguish them from the QC, metrics, counts, and
other output types generated through processing.
"""
from .sexcheck import SexChecker
