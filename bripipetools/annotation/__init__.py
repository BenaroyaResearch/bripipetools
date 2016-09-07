"""
Classes and methods for classifying and gathering information on data
objects produced by protocols, runs, and workflows.
"""
from .illuminaseq import FlowcellRunAnnotator, SequencedLibraryAnnotator
from .globusgalaxy import WorkflowBatchAnnotator, ProcessedLibraryAnnotator
