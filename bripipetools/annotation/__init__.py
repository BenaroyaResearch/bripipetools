"""
Includes critical functionality for identifying, locating, and
describing data and results at various points (e.g., data generation,
computational processing) in the bioinformatics pipeline. Each
"annotator" class, contained in its respective module, is
responsible for collecting and/or updating information for a specific
object in the GenLIMS database. When possible, details for an object
are retrieved directly from the database; for new objects or objects
with missing fields, information is compiled, parsed, and formatted
(as needed) from files on the server.
"""
from .sequencedlibs import SequencedLibraryAnnotator
from .librarygenecounts import LibraryGeneCountAnnotator
from .flowcellruns import FlowcellRunAnnotator
from .processedlibs import ProcessedLibraryAnnotator
from .workflowbatches import WorkflowBatchAnnotator

