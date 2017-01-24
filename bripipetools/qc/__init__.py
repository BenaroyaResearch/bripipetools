"""
Contains classes and methods for performing post-hoc quality control
operations on raw or processed genomics data. Modules are organized
according to the specifc QC step performed. Unlike routine quality
inspection metrics and information provided by standard bioinformatics
tools through processing workflows, modules here are aimed more at
identifying problems with sample handling or data generation. As such,
outputs from these submodules are designated as a special type,
'validation', to distinguish them from the QC, metrics, counts, and
other output types generated through processing.
"""
from .sexpredict import SexPredictor
from .sexverify import SexVerifier
from .sexcheck import SexChecker
