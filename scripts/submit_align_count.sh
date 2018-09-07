#!/bin/bash

# helper script to run bowtie and count reads via SLURM
# usage: submit_align_count.sh <bowtie idx> <query> <alignment outfile> <cts outfile>
bowtie -S $1 $2 $3

samtools view -F 260 $3 | cut -f 3 | sort | uniq -c | sort -n | awk '{printf("%s\t%s\n", $2, $1)}' > $4