#!/bin/sh
mkdir -p networks/degree
mkdir -p networks/distance
mkdir -p networks/random
mkdir -p test_results/degree
mkdir -p test_results/distance
mkdir -p test_results/random
mkdir -p test_results/simple_graphs

python3 concurrent_run.py -f simple_graphs_attacks_100x100.txt -g jobs-api.felipequintanilla.cl