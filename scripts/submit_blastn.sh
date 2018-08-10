#!/bin/bash

# helper script to run blastn via SLURM
# usage: submit_blastn.sh <db> <query> <outfile>
blastn -db $1 -query $2 -out $3 -outfmt 10