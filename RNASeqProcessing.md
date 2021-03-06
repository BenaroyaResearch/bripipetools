Processing fastq to counts using Globus Genomics Galaxy
===

1. Get the fastq data files
	+ **Prerequisite**: Illumina basespace account.
	+ Accept invitations for the flowcell (when run starts), and the Projects (at end)
	+ Download from Basespace using the basespace downloader helper app
	 	+ Vivian will have created the `/mnt/bioinformatics/pipeline/Illumina/{FlowcellID}` directory
	 	+ You need to make the Unaligned directory/folder: `% mkdir /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}/Unaligned`
		+ Download into `/mnt/bioinformatics/pipeline/Illumina/{FlowcellID}/Unaligned`
			+ Can be downloaded onto any machine that can mount /mnt/bioinformatics/pipeline (Linux), or 
			+ /Volumes/bioinformatics/pipeline (MacOS X)
			+ \\\\isilon.brivmrc.org\bioinformatics WinOS (set to I: drive)
	+ Optionally: inspect run QC at basespace website
	+ Project downloads can take a few minutes to an hour - an entire flowcell will take about 1-2 hrs to download, depending on the number of libraries, and sequencing technology.
	
**NB:** Starting in October 2017, the BaseSpace data directory structure changed slightly. The upshot is that if projects were run split between multiple lanes in a flowcell, the FASTQ files for these projects need to be placed in the correct folder. **It is now necessary to run the script `fix_fastq_paths.sh` before proceeding to process the flow cell.** If this script is _not_ run, there will be no error or indication that anything went wrong, but only one lane's worth of data will be processed per project. Command:

`bripipetools/scripts/fix_fastq_paths.sh /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}`


2. Create workflow batch file
	+ **Prerequisites:** Install Anaconda2; running bash; instance of bripipetools repository from github (your own copy, or the copy in `/mnt/bioinformatics/workspace/code/shared`)
	+ Make sure anaconda2/bin is in your path
	+ `% cd ~/git/bripipetools` (or the relevant repository location)
	+ `% source activate bripipetools` (activate is from anaconda2)
	+ **NB** - Make sure that the database configuration at `bripipetools/bripipetools/config/default.ini` is set correctly. 
		+ There need to be config entries in place for [database] and [researchdb]. 
		+ If you are using a local copy of GenLIMS and the Research Database, you will need to have a local instance of the mongo server daemon running (command: `mongod`).
		+ If you have questions about which database servers to use, please contact Mario Rosasco (mrosasco@benaroyaresearch.org).
	+ Create a batch submission file while in the bripipetools environment:
	+ `(bripipetools) bash-3.2$ bripipetools submit --workflow-dir /mnt/bioinformatics/pipeline/galaxy_workflows/ /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}` You may need to use the `--all-workflows` option if you want to use a non standard workflow.
	+ Select projects that have used the same technology, strandedness, and reference genome (or whatever combination you'd like).  The result is a workflow batch file.
	+ Don't worry if the path doesn't look right, use the path that looks like /mnt/bioinformatics/pipeline..., this is how it will appear on the machine that Globus Genomics uses for access (srvgridftp02).

3. Prepare Globus transfer endpoint
	+ **Prerequisite**: Globus ID account
	+ Authenticate at [Globus](https://app.globus.org/endpoints) with your globusid credentials
	+ Click on "Endpoints" at the left of the screen if you're not already there.
	+ Click on "benaroyaresearch#BRIGridFTP," then "Activate". 
	+ Enter your BRI credentials, and be sure to click "advanced" and set Credential Lifetime to 10,000hrs (this will get you the 7 day max of authentication).

4. Upload workflow batch file to Globus Genomics (from step 2)
	+ Go to the [BRI instance of Globus Genomics](https://bri.globusgenomics.org/)
	+ Under 'DATA TRANSFER', (top, left menu) look for 'Get Data via Globus'
	+ Cut and paste in the /mnt/bioinformatics/pipeline... path for the workflow data file that was generated in step 2.
	+ You will be using globus to upload the workflow batch file.

5. Submit uploaded workflow batch file - start processing the data
	+ Again, at the [BRI instance of Globus Genomics](https://bri.globusgenomics.org/)
	+ Under 'DATA MANAGEMENT' (near bottom, left menu) look for 'Workflow batch submit'
	+ select the base filename you uploaded in step 4.
	+ You will be triggering the batch application of workflows to the libraries from the projects projects you selected in step 2.

6. Wait for data to upload, process, then download
	+ The entire batch will take on the order of 24hrs to process, depending on the number of libraries and the size of the fastq files.
	+ There will be a history for each library workflow processed.  Use the gear (upper right) to refresh 'Saved Histories' to inspect the running workflows. You can see the number of steps that have been completed, are running, and are still pending for each library+workflow.
	+ Watch for red boxes, indicating a failed step - most times it's a transfer step, which you can manually re-trigger to complete (not a fatal error, just resubmit).

7. Post Processing
	+ Run these operations within `bripipetools` repostory, either on your own machine, or on srvgalaxy01.  If you are on a Mac, the leading mount may start with `/Volumes` instead of `/mnt`. 
	+ **NB** - Once again, make sure that the database configuration at `bripipetools/bripipetools/config/default.ini` is set correctly. 
	+ Concatenate trinity results:
		+ `% while read path; do python scripts/concatenate_trinity_output.py $path; done < <(find /mnt/bioinformatics/pipeline/Illumina/{FlowcellID} -name "Trinity" -maxdepth 2)`
	+ Or for a single Project:
		+ `% python scripts/concatenate_trinity_output.py /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}/{ProjectID}/Trinity`
	+ If a TCR based run, then run mixcr as well (**must** be done on srvgalaxy01 to use SLURM):
		+ **NB** - In order for SLURM to run properly, it needs write privileges for a slurm.out file in the directory it's executed from. The easiest way to ensure this is to call the SLURM/MiXCR command from /mnt/bioinformatics/pipeline/Illumina and allow SLURM to append to the existing slurm.out file there.
		+ **NB** - The following command assumes that all of the projects you're running MiXCR on identifying **human** TCRs. If you are analyzing mouse TCRs, or if there are both human and mouse TCRs on the same flow cell, you need to specify the species to MiXCR using the `-s` option with either `mmu` (mouse) or `hsa` (human) as appopriate. Note that in the case of both species on the same flow cell, the `run_mixcr.py` script can be called on each project's Trinity folder outside of the loop.
		+ `% while read path; do outdir="$(dirname $path)/mixcrOutput_trinity"; python /mnt/bioinformatics/workspace/code/shared/bripipetools/scripts/run_mixcr.py -i $path -o $outdir; done < <(find /mnt/bioinformatics/pipeline/Illumina/{FlowcellID} -name "Trinity" -maxdepth 2)`
		+ Generate a summary file of the productive TCR chains found in each library:
		+ `% Rscript --vanilla /mnt/bioinformatics/workspace/code/shared/bripipetools/scripts/summarize_mixcr_output.R /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}`
	+ Wrap up the processing, stitching together files, inserting data into tg3 with:
		+ `% bripipetools wrapup /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}/`
	+ Watch for missing files in the output of wrapup - select no, if there are missing files, and go back to galaxy and re-transfer if necessary, or recreate from above.
	+ In order to call SNPs for a flow cell run, you can run the `scripts/call_snps.sh` script. Running this script without any arguments will give you usage information.
	+ If the run contains SNP data you can perform kinship analysis to identify potential sample swaps:
		+ `% scripts/calculate_kinship.sh -d /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}/`
	+ Finally, create the gene metrics plots:
		+ `% while read path; do python scripts/plot_gene_coverage.py $path/; done < <(find /mnt/bioinformatics/pipeline/Illumina/{FlowcellID} -name "metrics" -maxdepth 2)`
	+ Once the projects are processed, you can use the following script to generate a list of project links to send to the appropriate analysts:
		+ `% scripts/generate_project_links.sh /mnt/bioinformatics/pipeline/Illumina/{FlowcellID}`

8. Backup Illumina run data
	+  Mount Illumina basespace data using the basemount tool (uses Linux userspace mount). The first time you use it you will need to authenticate to the Illumina servers.  See: [Illumina Basemount](https://basemount.basespace.illumina.com/) for vidoes, documentation and the like. Perform all actions as unprivilaged user (not root, do not sudo).
		+ `% basemount ~/basespace_mount`
	+ Backup to local storage (from /mnt/bioinformatics/workspace/code/shared/bripipetools):
		+ `% python /mnt/bioinformatics/workspace/code/shared/bripipetools/scripts/backup_basespace.py ~/basespace_mount/ /mnt/bioinformatics/pipeline/Illumina/basespace_backup`
	+ Finally, unmount the Illumina basespace data
		+ `% basemount --unmount ~/basespace_mount`
		
9. Gotchas:
	+ There are permissions under `/mnt/bioinformatics/pipeline/Illumina/{FlowCellID}` that you'll need to keep an eye on. Specifically:
	+ Make sure you are in group NAS_BIOINF1 (check with `% id` or `% groups`)
	+ Make sure you have write access to the flowcell directory - your credentials will be used to create directories and download files from Globus Genomics on your behalf.
	+ For the mixcr run, make sure slurm.out is writeable by you (or the world). This is easiest to achieve by running the `run_mixcr.py` script from the `/mnt/bioinformatics/pipeline/Illumina/` directory. 
