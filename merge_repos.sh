#!/bin/sh

# assign inputs
REPO=$1
SUB_DIR=$2
BRANCH=$3

CURRENT_DIR=${PWD##*/}

echo "Merging GitHub repository:"
echo "$REPO"
echo "into $CURRENT_DIR as:"
echo "$SUB_DIR/"

git remote add -f $SUB_DIR git@github.com:jaeddy/${REPO}
git merge -s ours --no-commit ${SUB_DIR}/${BRANCH}
git read-tree --prefix=${SUB_DIR} -u ${SUB_DIR}/${BRANCH}
git commit -m "subtree merged in ${SUB_DIR}"