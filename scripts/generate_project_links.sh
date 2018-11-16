#!/bin/bash

FC_DIR=${1%/}

while read proj_dir; do
    proj=$(echo $proj_dir | egrep "P[0-9]+(-[0-9]+)*" -o)
    echo $proj
    smb_path=$(echo $proj_dir | awk '{gsub(/\/(mnt|Volumes)/, "smb://isilon.brivmrc.org")}1')
    echo "Mac: ${smb_path}"
    win_path=$(echo $smb_path | awk '{gsub("smb:", "")}1' | awk '{gsub("/", "\\")}1' | sed 's/.brivmrc.org//')
    echo "Windows: ${win_path}"
    echo " "

done < <(find $FC_DIR -maxdepth 1 -name "Project_P*Processed*" | sort)
