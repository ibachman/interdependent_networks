#!/bin/sh
mkdir -p test_results/degree
mkdir -p test_results/distance
mkdir -p test_results/random
mkdir -p test_results/simple_graphs

pip3 install -r requirements.txt

python3 job_manager.py -f all_experiments.txt -w 88