#!/bin/bash

DATA_ROOT="/Volumes"
TEST_ROOT="tests/test-data"

FC_FOLDER="genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/Unaligned"
FC_PATH="${DATA_ROOT}/${FC_FOLDER}"

TEST_PATH="${TEST_ROOT}/${FC_FOLDER}"

while read project_folder; do
    project_name=$(basename $project_folder)
    test_project="${TEST_PATH}/${project_name}"
    echo "Creating $test_project folder..."
    mkdir $test_project

    while read lib_folder; do
	lib_name=$(basename $lib_folder)
	test_lib="${test_project}/${lib_name}"
	echo "Creating $test_lib folder..."
        mkdir $test_lib

	while read lib_file; do
            file_name=$(basename $lib_file)
            test_file="${test_lib}/${file_name}"
            echo "Creating $test_file dummy file..."
            touch $test_file
        done < <(find $lib_folder -mindepth 1 -maxdepth 1 | grep -v "empty")

    done < <(find $project_folder -type "d" -mindepth 1 -maxdepth 1 | head -5)

done < <(find $FC_PATH -type "d" -mindepth 1 -maxdepth 1)
