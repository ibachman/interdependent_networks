#!/bin/sh
mkdir -p networks/degree
mkdir -p networks/distance
mkdir -p networks/random
mkdir -p test_results/degree
mkdir -p test_results/distance
mkdir -p test_results/random
mkdir -p test_results/simple_graphs

if [ -z "$ATK_FILE_URI" ]
then
      echo "\$ATK_FILE_URI is empty, using existing attacks file"
else
      echo "\$ATK_FILE_URI is NOT empty"
	  aws s3 cp $ATK_FILE_URI simple_graphs_attacks_100x100.txt
fi

python3 -u concurrent_run.py -f simple_graphs_attacks_100x100.txt -g jobs-api.felipequintanilla.cl

if [ -z "$RESULTS_BUCKET_URI" ]
then
      echo "\$RESULTS_BUCKET_URI is empty, exiting without uploading results"
else
      echo "\$RESULTS_BUCKET_URI is NOT empty"
	  find test_results -type f -print | xargs -I {} aws s3 cp {} $RESULTS_BUCKET_URI/{}
fi

