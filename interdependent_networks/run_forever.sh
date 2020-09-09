#!/bin/sh
mkdir -p networks/degree
mkdir -p networks/distance
mkdir -p networks/random
mkdir -p test_results/degree
mkdir -p test_results/distance
mkdir -p test_results/random
mkdir -p test_results/simple_graphs

if [ -z "$MACHINE_NAME" ]
then
	WORKER_NAME=`hostname`
else
    WORKER_NAME=$MACHINE_NAME
fi

python3 -u job_manager.py -g jobs-api.felipequintanilla.cl -m ${WORKER_NAME}

