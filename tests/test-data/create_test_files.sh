#!/bin/bash

DATA_ROOT="/Volumes"
TEST_ROOT="tests/test-data"

#FC_FOLDER="genomics/Illumina/150615_D00565_0087_AC6VG0ANXX/Unaligned"
FC_FOLDER=$1
FC_PATH="${DATA_ROOT}/${FC_FOLDER}"


TEST_PATH="${TEST_ROOT}/${FC_FOLDER}"
TEST_READ_DEPTH=100000

while read project_folder; do
    project_name=$(basename $project_folder)
    test_project="${TEST_PATH}/${project_name}"
    echo "Creating $test_project folder..."
    mkdir -p $test_project

    while read lib_folder; do
	lib_name=$(basename $lib_folder)
	test_lib="${test_project}/${lib_name}"
    num_files=$(find $lib_folder -mindepth 1 -maxdepth 1 \
                | grep -v "empty" \
                | wc -l)
    num_fq_lines=$(expr $TEST_READ_DEPTH / $num_files \* 4)
	echo "Creating $test_lib folder..."
        mkdir $test_lib

	    while read lib_file; do
            file_name=$(basename $lib_file)
            test_file="${test_lib}/${file_name}"
            test_file=${test_file%%.*}
            echo "Creating sub-setted file $test_file..."
            gzcat $lib_file | head -$num_fq_lines > $test_file \
                && gzip -9 $test_file
        done < <(find $lib_folder -mindepth 1 -maxdepth 1 | grep -v "empty")

    done < <(find $project_folder -type "d" -mindepth 1 -maxdepth 1 | head -3)

done < <(find $FC_PATH -type "d" -mindepth 1 -maxdepth 1)
