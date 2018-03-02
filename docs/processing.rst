.. _process-page:

***************
Processing data
***************

Data processing is the primary function of **bripipetools**, encompassing all bioinformatics operations performed on raw data (typically sequencing libraries) to generate processed output files. BRI processing pipelines do not include statistical analyses performed on output data.

.. _process-workflows:

Workflows
=========

Workflows are the heart of bioinformatics processing operation. They comprise a repeatable series of steps performed on a collection of data files. Steps within a workflow can be broken down or categorized into specific modules, depending on the goal or output of the step.

Processing modules
------------------

data QC
^^^^^^^

Quality control refers to basic inspection and computation of quality metrics/statistics for *raw* sequencing data. Of course, quality assessment can and should occur at multiple stages from data generation to analysis. However, due to historical reasons, "QC" in the context of the pipeline almost exclusively implies tools and outputs related to the characteristics of FASTQ files. The *de facto* tool for this step is **FastQC - ADD LINK!!!** (and should continue to be for the forseeable future). Elements of raw sequencing data QC not covered by FastQC that might be worth incorporating in future versions of the pipeline include library complexity (maybe that's it?).

Current tool: ``FastQC``

trimming
^^^^^^^^

Trimming here refers to "hard trimming" of a fixed number of bases from raw sequencing reads. A nearly universal characteristic of sequencing data from the BRI Genomics Core is an unexpected spike in GC skew at the last position (on the 3' end) of reads **INCLUDE SCREENSHOT**. For this reason, the first step in most workflows is the removal of the last 3' base from each read.

Current tool: ``FASTQ Trimmer``

adapter trimming
^^^^^^^^^^^^^^^^

For certain library prep procedures (e.g., Nextera), oligonucleotide indexes will be included as part of the PCR amplifcation step, prior to library construction. In these cases, these adapter sequences will appear within reads, in contrast to typical sequencing adapters (e.g., Illumina adapters and indexes used for demultiplexing) that are nominally removed by tools like **CASAVA** and **bcl2fastq**.

Current tool: ``FastqMcf``

quality trimming
^^^^^^^^^^^^^^^^

Modern aligners use "dynamic" or "adaptive" trimming to remove bases from either end of individual reads to improve mapping to the reference. Reads can also be pre-processed to remove bases that do not pass a certain quality threshold. In theory, removing low quality (and thus, low confidence) bases can also improve mapping rate; however, care must be taken to impose a minimum length for trimmed reads, as extremely short reads will lead to high duplication rates and biased results.

Current tool: ``FASTQ Quality Trimmer``

alignment
^^^^^^^^^

This is the central step for almost all NGS processing workflows. Following any trimming, short reads are aligned to a reference genome and the results are stored in a Sequence Alignment Map (SAM) file — and more typically, in the binary BAM format. For RNA-seq data, it is important to use aligners that are "splice aware" (e.g., **TopHat** and **STAR**) to account for the fact that reads from mRNA transcripts may include one or more exons that are not adjacent in the genome (and therefore might not align). Alternatively, RNA reads could be aligned to a reference transcriptome.

In summer of 2018, after multiple comparisons between STAR-aligned and TopHat-aligned libraries, we decided to transition our workflows to STAR from TopHat.

Current tools: ``STAR``

Previous tools: ``TopHat``

counting
^^^^^^^^

After reads have been aligned to the genome, reference annotations (i.e., gene models) can be used to inspect and quantify read coverage within regions of interest (e.g., exons).

Current tool: ``htseq-count``

quantification
^^^^^^^^^^^^^^

Current tool: ``salmon``


SNP fingerprinting
^^^^^^^^^^^^^^^^^^

Current tools: ``samtools``, ``bcftools``

metrics
^^^^^^^

Unlike **QC**, "metrics" is a catch-all category to describe any summary or quality measures of post-alignment data. The primary source of metrics is the **Picard** suite of tools for evaluating alignment in SAM/BAM files. For downstream tools that produce reports or logs (e.g., **htseq-count**), outputs are also categorized and stored under metrics.

Current tools: ``Picard``


VDJ annotation
^^^^^^^^^^^^^^

Many projects (eg: scRNAseq projects) involve identification of TCR sequences. To achieve sequencing of these highly polymorphic sequences, we first perform a de novo assembly using **Trinity** (see below), and then use **MiXCR** to identify the TCR chains from the assembly.

Current tools: ``mixcr``


assembly
^^^^^^^^

For experiments where it doesn't make sense to align to a reference (eg: no reference available, huge number of polymorphisms), we perform a de novo assembly of the reads. This essentially aligns the reads to one another in a series of steps, building long sequences representing transcripts from the short reads of fragments. These long transcript sequences can then be used for a number of purposes, such as building a transcriptome, or aligning transcripts with partially conserved and partially variable regions (as in TCR identification).

Current tools: ``Trinity``


variant calling
^^^^^^^^^^^^^^^

Current tools: ``samtools``, ``bcftools``


-----


.. _process-options:

Workflow options
================

The following workflows are currently available for batch processing in Globus Genomics.

TruSeq, Stranded, STAR (with or without Trinity)
Nextera, Non-stranded, STAR (with or without Trinity)

**Deprecated Workflows**
TruSeq, Stranded, TopHat (with or without Trinity)
Nextera, Non-stranded, TopHat (with or without Trinity)


-----


.. _process-compose:

Composing a workflow
====================

(in Globus Galaxy)

Implementing a new (production) workflow in Globus Galaxy consists of two steps: building a new workflow and annotating all input and output steps.

Building a workflow in Galaxy
-----------------------------

Use the Workflow Editor in Globus Galaxy for the following steps:

1. Add all tools for processing modules (e.g., trimming, alignment, counting).
2. Connect inputs and outputs of individual tools.
3. Add workflow inputs:
   1. Get Globus FASTQ data
   2. Input Dataset (for reference/annotation files)
4. Add workflow outputs (Send Globus data)
5. Set all get/send data endpoint and path options to 'set at runtime'
6. (optional) Set build-specific and other options to 'set at runtime'
7. Annotate input and output steps (and potentially build-specific parameters)

Annotating parameters
---------------------

For all parameters where values are to be set at runtime :superscript:`*`, tags of the following format should be added to the **Annotation / Notes** field in the Globus Galaxy Workflow Editor.

:superscript:`*` "option" parameters are recognized by the combination of their ``tag`` (in the **Annotation** field) as well as their **name** which is assigned by Galaxy.

Input parameters
^^^^^^^^^^^^^^^^

Input parameters — indicating local files that will be uploaded to Globus Galaxy nodes at the start of workflow processing — should have the following form:

``extension_in``

This typically only applies to ``fastq_in``.

Output parameters
^^^^^^^^^^^^^^^^^

Output parameters are expected to have the following form:

``<source>_<type>_<extension>_<out>``

For example, the tag ``picard-rnaseq_metrics_html_out`` will be parsed into a dictionary like this:::

    {
        'type': 'metrics',
        'label': 'metrics',
        'source': 'picard-rnaseq',
        'extension': 'html'
     }

Both source and label can be given added specificity with a hyphen-separated string (e.g., ``picard`` vs. ``picard-rnaseq`` or ``metrics`` vs. ``metrics-rmdup``). The parsing code should automatically detect and group these clauses appropriately.

Annotation input paramters
^^^^^^^^^^^^^^^^^^^^^^^^^^

Some workflows will access and load datasets stored in the Globus Galaxy library. These inputs (represented as **Input Dataset** in the workflow editor) should have annotation tags in the following form:

``annotation_<type>``

You can also give a name to the dataset to possibly ease navigation within the editor, but these names will not be used by downstream code.

The most common annotation input parameters are the following:

* GTF gene model files: ``annotation_gtf`` (optional name: ``gtfFile``)
* Gene model refFlat files: ``annotation_refflat`` (optional name: ``refFlatFile``)
* Ribosomal interval files: ``annotation_ribosomal-intervals`` (optional name: ``riboIntsFile``)
* Adapter files: ``annotation_adapters`` (optional name: ``adapterFile``)


Saving the workflow template
----------------------------

Once a workflow is finished and ready for testing...

1. Click the arrow next to the workflow name in the Galaxy **Workflows** tab.
2. Select "Submit via API batch mode".
3. On the following page, click the link to "Export Workflow Parameters for batch submission" and save the file under ``genomics/galaxy_workflows`` (wherever the path exists relative to your local system); make sure to remove the leading ``Galaxy-API-Workflow-`` from the filename.


Importing a new workflow to GenLIMS
-----------------------------------

**[PROPOSED]** The following ideas have not been implemented in GenLIMS or **bripipetools**; skip for now.

Importing a workflow requires two inputs: the exported workflow JSON and the corresponding API batch submission template. This will create a new document in the **workflows** collection with 5 initial fields:

1. ID
2. exportedWorkflow: the full JSON description of the workflow, as exported from Globus Galaxy; this typically won't be needed unless details about individual tools are desired
3. batchSubmit: this field stores the building blocks of the API batch submission template, including header content, metadata fields, and parsed workflow parameters
4. modules: auto-parsed from batch submit parameters; these key-value pairs describe output types (e.g., counts, alignment) and the corresponding tools used in the workflow
5. type: either "Galaxy workflow" or "Globus Galaxy workflow"

Next, you will be prompted to select fill in additional information indicating the function of the workflow, compatible input data types, and available references. These fields can be edited later in the browser, but are required for semi-automated selection of workflows when submitting new batches.

5. protocols
6. input (libPrep, species, single/paired)
7. refs

Finally, if importing an "optimized" workflow, you will be asked to indicate so and provide the name/ID of the corresponding base workflow. Additionally, if there is a non-Globus Galaxy workflow that matches the imported workflow, that can be indicated as well.

-----


.. _process-run:

Running a workflow
==================

All of the following steps except the initial **BaseSpace** download should work while on ``srvgalaxy01``.

Pipeline steps
--------------

1. [Downloading & prepping data](## Downloading & prepping data)
2. [Getting data into Galaxy](## Getting data into Galaxy)
3. [Running a workflow](## Running a workflow)
4. [Getting data out of Galaxy](## Getting data out of Galaxy)

Downloading & prepping data
---------------------------

When a new flow cell is ready for processing, a notification email is sent from the **Genomics Core** via **BaseSpace**. Information about the flowcell and corresponding projects can be found in the ``Flowcell log.xlsx`` file under ``DFS_Chaussabel_LabShare/Illumina HiScan SQ/`` on the [``srvstor01``](srvstor01.brivmrc.org) server. In particular, you'll need to pay attention to the ``Lane Contents`` tab to determine the appropriate workflow to use for each project.

On ``srvgalaxy01`` under ``/mnt/genomics/Illumina/<flowcell-folder>/``, create a new folder called ``Unaligned/`` (if it doesn't already exist). Modify permissions such that all users can write to and read from the folder (``chmod -R 777 Unaligned/``). The new folder should look something like this:

::

    FC_FOLDER="/mnt/genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/Unaligned"


Using ``bripipetools``
----------------------

The ``bripipetools`` command (which calls ``bripipetools/__main__.py``) is the entrypoint to application functionality. If you have the **bripipetools** package installed, you should be able to use this command from anywhere on your system.
::

    bripipetools --help

::

    Usage: bripipetools [OPTIONS] COMMAND [ARGS]...

      Command line interface for the `bripipetools` library.

    Options:
      --quiet  only display printed outputs in the console - i.e., no log messages
      --debug  include all debug log messages in the console
      --help   Show this message and exit.

    Commands:
      dbify        Import data from a flowcell run or workflow...
      postprocess  Perform postprocessing operations on outputs...
      qc           Run quality control analyses on a target...
      submit       Prepare batch submission for unaligned...
      wrapup       Perform 'dbify' and 'postprocess' operations...




Preparing workflow batches for submission
-----------------------------------------

At this point, you'll need to identify the most applicable workflow (for a more detailed guide on selecting workflows, see the [**workflows** doc](workflows.md)).

Refer to flowcell log
^^^^^^^^^^^^^^^^^^^^^

The flowcell log can be found at ``DFS_Chaussabel_LabShare/Illumina HiScan SQ/Flowcell log.xlsx``.

Using ``bripipetools`` to submit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    bripipetools submit --help

::

    Usage: bripipetools submit [OPTIONS] PATH

      Prepare batch submission for unaligned samples from a flowcell run or from
      a list of paths in a manifest file.

    Options:
      --endpoint TEXT                 Globus Online endpoint where input data is
                                      stored and outputs will be saved
      --workflow-dir TEXT             path to folder containing Galaxy workflow
                                      template files to be used for batch
                                      processing
      --all-workflows / --optimized-only
                                      indicate whether to include all detected
                                      workflows as options or to keep 'optimized'
                                      workflows only
      -s, --sort-samples              sort samples from smallest to largest (based
                                      on total size of raw data files) before
                                      submitting; this is most useful when also
                                      restricting the number of samples
      -n, --num-samples INTEGER       restrict the number of samples submitted for
                                      each project on the flowcell
      -m, --manifest                  indicates that input path is a manifest of
                                      sample or folder paths (not a flowcell run)
                                      from which a workflow batch is to be created
                                      (note: options 'sort-samples' and 'num-
                                      samples' will be ignored)
      -o, --out-dir TEXT              for input manifest, folder where outputs are
                                      to be saved; default is current directory
      --help                          Show this message and exit.



Here's an example call:::

    bripipetools submit \
        --workflow-dir /mnt/genomics/galaxy_workflows \
        --endpoint jeddy#srvgridftp01
        /mnt/genomics/Illumina/150615_D00565_0087_AC6VG0ANX


Here's another example with a manifest file::

    bripipetools submit \
        --workflow-dir /Volumes/genomics/galaxy_workflows/ \
        --out-dir /Volumes/genomics/ICAC/Gern/ -\
        -tag gern \
        --manifest <(find /Volumes/genomics/ICAC/Gern -name "Sample_*")


Submitting batches in Globus Genomics
-------------------------------------

Authenticating Globus endpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, sign in to Globus Online and navigate to the **Manage Data** page. In the field for "Endpoint", select ``jeddy#srvgridftp01``, after which you'll be prompted to enter your login credentials for the ``srvgridftp01`` BRI server. Make sure to expand the "advanced" options and set the "Credential Lifetime" to 10000 hours (that way, you won't need to reauthenticate for about a week).


Uploading batch submit files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

(steps)

Submitting batch jobs
^^^^^^^^^^^^^^^^^^^^^

(steps)

Collecting workflow batch results
---------------------------------

::

    Usage: bripipetools wrapup [OPTIONS] PATH

      Perform 'dbify' and 'postprocess' operations on all projects and workflow
      batches from a flowcell run.

    Options:
      -t, --output-type [c|m|q|v|a]   type of output file to combine: c [counts],
                                      m [metrics], q [qc], v [validation], a [all]
      -x, --exclude-types [c|m|q|v]   type of output file to exclude: c [counts],
                                      m [metrics], q [qc], v [validation]
      --stitch-only / --stitch-and-compile
                                      Do NOT compile and merge all summary (non-
                                      count) data into a single file at the
                                      project level
      --clean-outputs / --outputs-as-is
                                      Attempt to clean/organize output files
      --help                          Show this message and exit.


Importing flowcell data into GenLIMS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Usage: bripipetools dbify [OPTIONS] PATH

      Import data from a flowcell run or workflow processing batch into GenLIMS
      database.

    Options:
      --help  Show this message and exit.


Postprocessing workflow outputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    Usage: bripipetools postprocess [OPTIONS] PATH

      Perform postprocessing operations on outputs of a workflow batch.

    Options:
      -t, --output-type [c|m|q|v|a]   type of output file to combine: c [counts],
                                      m [metrics], q [qc], v [validation], a [all]
      -x, --exclude-types [c|m|q|v]   type of output file to exclude: c [counts],
                                      m [metrics], q [qc], v [validation]
      --stitch-only / --stitch-and-compile
                                      Do NOT compile and merge all summary (non-
                                      count) data into a single file at the
                                      project level
      --clean-outputs / --outputs-as-is
                                      Attempt to clean/organize output files
      --help                          Show this message and exit.


Follow up steps
---------------

Not all pipeline steps have been integrated into the ``bripipetools`` application code base. Remaining steps are performed with scripts located in the ``scripts`` folder.

Generating gene model coverage plots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    usage: plot_gene_coverage.py PATH


::

    while read path; do \
        python scripts/plot_gene_coverage.py $path;
    done < <(find <path-to-flowcell-folder> -name "metrics" -maxdepth 2)


Running MiXCR (depending on workflow version)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Note: requires SLURM!! (must run on server ``srvgalaxy01``)

::

    /mnt/code/shared/bripipetools/

::

    usage: run_mixcr.py [-h] -i INPUTDIR -o RESULTSDIR


::

    while read path; do \
        outdir="$(dirname $path)/mixcrOutput_trinity";
        python scripts/run_mixcr.py -i $path -o $outdir;
    done < <(find <path-to-flowcell-folder> -name "Trinity" -maxdepth 2)



Handy shortcut:::

    # Custom formatted output from squeue
    alias squeuel='squeue -o "%.7i %.9P %.30j %.10u %.8T %.10M %.6D %.5C %.8p %R"'


Concatenating Trinity outputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    usage: concatenate_trinity_output.py PATH

::

    while read path; do \
        python scripts/concatenate_trinity_output.py $path;
    done < <(find <path-to-flowcell-folder> -name "Trinity" -maxdepth 2)


Generating project links
^^^^^^^^^^^^^^^^^^^^^^^^

::

    usage: generate_project_links.sh PATH

::

    bash scripts/generate_project_links.sh <path-to-flowcell-folder>


Inspecting outputs
^^^^^^^^^^^^^^^^^^

After running the `pulldownGalaxyData.py` script, results will be stored under the flowcell folder in a new folder that looks like `Project_<project-id>Processed_<date>`, where date is the YYMMDD string of the date on which the *script* was run — e.g., `Project_P43-12Processed_151208`.


-----

.. _processing-local:

Retrieving details for old workflows
====================================

To collect details about old workflows and histories from processing jobs on the local Galaxy server, one can either use the **PostgreSQL** database directly, or take advantage of an **R** script for interacting with the database.

Galaxy PostgreSQL database queries
----------------------------------

Keeping track of various queries here with thought of eventually combining into scripts or functions.

Basic login to db:::

    svc_galaxy@srvgalaxy02:~$ psql svc_galaxy

History info for a project:::

    svc_galaxy=# select * from history where name like '%P15-8%';

::

    svc_galaxy=# select id from history where name like '%P15-8%';


Dataset info for a specific History
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

List datasets:::

    svc_galaxy=# SELECT dataset_id FROM history_dataset_association WHERE history_id = '536';


Get full dataset info:::

    svc_galaxy=# SELECT * FROM dataset WHERE id IN (SELECT dataset_id FROM history_dataset_association WHERE history_id = '536');


Job info for a specific History
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    svc_galaxy=# SELECT * FROM job WHERE history_id = '536';


Job metrics for specific steps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    svc_galaxy=# SELECT * FROM job_metric_numeric WHERE job_id IN (SELECT id FROM job WHERE history_id = '529' AND tool_id LIKE '%/tophat/%') AND metric_name = 'runtime_seconds';



Job metrics for datasets
^^^^^^^^^^^^^^^^^^^^^^^^

::

    svc_galaxy=# SELECT * FROM job_to_input_dataset WHERE dataset_id IN (SELECT dataset_id FROM history_dataset_association WHERE history_id = '536');


Magic R notebook
----------------

(``flowcell_qc_check`` repo)

``galaxy_history_annotation.Rmd``
