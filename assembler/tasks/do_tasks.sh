#!/bin/bash

MAX_NUMBER_OF_INPUT_FILES="3"
TARGET_ID=$(date +%Y%m%d_%H%M)

SOURCE=/app/assembler/tasks/shared_phrases/
INPUT_FILES=`ls -1 ${SOURCE} | sort -r | head -${MAX_NUMBER_OF_INPUT_FILES}`

DESTINATION=/app/assembler/tasks/shared_targets/${TARGET_ID}

[ ! -d ${DESTINATION} ] && (mkdir ${DESTINATION};)

for input_file in ${INPUT_FILES} ; do
    cp ${SOURCE}${input_file} ${DESTINATION}/${input_file}
done

cd /zookeeper/bin
./zkCli.sh -server zookeeper:2181 set /phrases/assembler/last_built_target ${TARGET_ID}