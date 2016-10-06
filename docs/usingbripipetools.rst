Using bripipetools
==================

Currently, there are three primary functions served by package modules:

- Generation of workflow instructions and submission of data processing batches
- Collection and organization of output data from bioinformatics processing workflows
- Annotation and import of pipeline input & output data into the Genomics Core Mongo database — i.e., **GenLIMS**

These features are continuing to expand and evolve over time.

Workflow batch submission
-------------------------

Batch submission to Globus Galaxy for bioinformatics data processing is currently managed through the script ``generate_fc_batch_submit.py``.

----

Post-processing
---------------

The entrypoint for tasks related to organizing processing output files (e.g., file stitching, cleanup, etc.) is the wrapper script ``bripipe-postprocess``, which uses the ``postprocess`` module.

-----

Data management
---------------

Annotation of sequencing and processing data — as well as corresponding retrieval and import of data from/to the GenLIMS database — is performed through the wrapper script ``bripipe-dbify``, which uses the ``dbify`` module.
