.. _process-10x:

*******************
Processing 10X Data
*******************

.. _cellranger-info:

Cell Ranger
=======================

Processing of 10X data is handled using the Cell Ranger platform, which comprises a series of pipeline scripts created and supported by 10X Genomics. 
Details about the Cell Ranger platform can be accessed from the `10X Genomics Website <https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/what-is-cell-ranger>`_.

It is possible to call Cell Ranger pipeline stages on the data directly, however the bripipetools package includes a script ``run_cellranger.sh`` to facilitate handling of BRI 10X data.
This script is a thin wrapper around the ``cellranger mkfastq``, ``cellranger count``, ``cellranger vdj``, and ``cellranger aggr`` programs. Details on this script can be found below.

.. _run-cellranger-script-requirements:

Requirements
============

The ``run_cellranger.sh`` script has the following requirements:

- bcl2fastq is installed
- Cell Ranger is installed
- There is a mount point for the genomics directory containing flow cell run data
- There is a mount point for the bioinformatics directory containing processed flow cell data

If the script is run from ``srvtenx02``, then these requirements will be satisfied. 

The script also assumes that the sample sheet for the run is located in the genomics run directory and is named SampleSheet.csv.

.. _run-cellranger-script-usage:

Usage
============

.. code-block:: sh
  
  ./run_cellranger.sh -h

      This program will run the full Cell Ranger pipeline for a list of
      BRI Genomics Core flow cell runs. This includes 'mkfastq' and either
      'count' or 'vdj' depending on the library type. The library type is
      determined based on the values in the 'Description' column of the sample
      sheet, which should have values of '10X_GEX' or '10X_TCR' as appropriate.
      As a final step, 'aggr' will be run on all gene expresion libraries,
      with the output added to the processing directory of the last flow cell
      run listed.

      NB - This program assumes that the sample sheet in the genomics run
      directory is appropriate to use for Cell Ranger processing, and is named
      'SampleSheet.csv'.

  Usage: ./run_cellranger.sh [options] <flow cell run list>
  Available Options:
  [-h] display help text then exit
  [-p <projectID>] default: P000-0
  [-n <procesingName>] default: CellRangerV4NoAdapterManual
  [-d <datePrefix>] default: current date in YYMMDD format
  [-v <cellRangerVersion>] default: 4.0.0
  [-a <aggrNormMethod>] default: none
  [-t <vdjReference>] default: .../refdata-cellranger-vdj-GRCh38-alts-ensembl-4.0.0
  [-g <gexReference>] default: .../GRCh38.91
  [-b <baseBfxDir>] default: /nfs/bioinformatics/pipeline/Illumina/
  [-q <baseGenomicsDir>] default: /nfs/genomics/Illumina/
  

.. _run-cellranger-script-example:

Example
============

Depending on the amount of data contained in the flow cell runs, the script may take several hours to complete.
As a result, it is often useful to run this script with ``nohup`` and collect the diagnostic output into a log file for later reference.

.. code-block:: sh

  nohup ~/bripipetools/scripts/run_cellranger.sh \
  -p "P365-1" \
  -n "CellRangerScriptTest" \
  200811_VH00126_26_AAACCGWM5 > \
  /nfs/bioinformatics/pipeline/Illumina/200811_VH00126_26_AAACCGWM5/CellRangerScriptTest.log

