#!/bin/bash

##
# Take emails out of the undeliverable queue and dump them in the accepted queue for reprocessing
##

cd `readlink -e router/run`

TMP_DIR=tmp
IN_QUEUE=undeliverable/new
OUT_QUEUE=accepted/new

mkdir -p $TMP_DIR

for file in $IN_QUEUE/*
do
    name=`basename $file`
    grep -v X-Queue-Retry $file > $TMP_DIR/$name && rm $file
done

for file in $TMP_DIR/*
do
    mv $file $OUT_QUEUE
done

echo "Done."
