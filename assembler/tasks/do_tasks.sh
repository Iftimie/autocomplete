#!/bin/bash

MAX_NUMBER_OF_INPUT_FILES="3"
TARGET_ID=$(date +%Y%m%d_%H%M)

# Wait for phrases
echo "Checking if /phrases/1_sink/phrases/ exists.."
while ! $(hadoop fs -test -d "/phrases/1_sink/phrases/") ; do echo "Waiting for folder /phrases/1_sink/phrases/ to be created by kafka connect. Please wait.."; done
echo "Checking for contents in /phrases/1_sink/phrases/.."
while [[ $(hadoop fs -ls /phrases/1_sink/phrases/ | sed 1,1d) == "" ]] ; do echo "Waiting for kafka connect to populate /phrases/1_sink/phrases/*. Please wait.."; done

hadoop fs -mkdir -p /phrases/2_targets/${TARGET_ID}/
INPUT_FOLDERS=`hadoop fs -ls /phrases/1_sink/phrases/ | sed 1,1d | sort -r -k8 | awk '{print \$8}' | head -${MAX_NUMBER_OF_INPUT_FOLDERS} | sort`
for input_folder in ${INPUT_FOLDERS} ; do
    hdfs dfs -cp ${input_folder} /phrases/2_targets/${TARGET_ID}/ ;
done

cd /zookeeper/bin
./zkCli.sh -server zookeeper:2181 set /phrases/assembler/last_built_target ${TARGET_ID}