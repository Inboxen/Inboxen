#!/bin/bash

set -e

lasttag=`git describe --abbrev=0`
changes=`git log $lasttag..HEAD --oneline | sed 's/^/# /'`
tmpfile=`mktemp`
changelog=`mktemp`
today=$1
underline=`echo $today | sed 's/./=/g'`

cat <<EOF > $tmpfile
Deploy for $today
===========$underline

# List changes here to add them to the tag and changelog
# Lines starting with a '#' will be ignored
#
# Changes since $lasttag
#
$changes
EOF

vim $tmpfile

printf "\n%s\n" "$(cat $tmpfile | sed '/^#/d')" > $changelog
sed -i -e "/Releases/r $changelog" CHANGELOG.md

git tag -as -F $changelog deploy-$today

rm $tmpfile $changelog
