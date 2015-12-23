#!/usr/bin/env bash
# extract_and_move: Extract files from <src> and move them under <dest>
if [ ! $# -eq 2 ]
then
  echo "./extract_and_move <src> <dest>"
exit 1
fi

SRC=$1
DEST=$2
DEST_FIRST=${DEST%%\/*}

# Extract $SRC, put them at the project root
git filter-branch -f --prune-empty --subdirectory-filter $SRC -- HEAD

# Move them under $DEST
git filter-branch -f --prune-empty --tree-filter "mkdir -p $DEST; find . -mindepth 1 -maxdepth 1 | grep -v ${DEST_FIRST} | grep -v '^./.git' | xargs -I {} mv {} ./$DEST" HEAD

