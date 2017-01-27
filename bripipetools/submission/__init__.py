"""
Prepares data for batch submission through Globus Galaxy, typically
starting from unaligned samples (libraries) from a flowcell run. The
``submission.batchcreate`` and ``submission.batchparameterize``
modules handle most of the work: the first takes a list of sample
paths (or folders containing sample paths) and a workflow template
file and controls the preparation of a batch submit file as well as
target folders for batch outputs; the latter sets individual
parameter values (mostly input and output file paths) for each sample,
which are then used by the ``BatchCreator`` class to create and write
the overall submission instructions. The ``submission.flowcellsubmit``
module provides a wrapper around ``batchcreate``, allowing a user to
select workflows and generate batch submissions for multiple unaligned
projects from a flowcell run.
"""
from .batchparameterize import BatchParameterizer
from .batchcreate import BatchCreator
from .flowcellsubmit import FlowcellSubmissionBuilder
from .samplesubmit import SampleSubmissionBuilder