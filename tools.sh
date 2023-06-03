#!/bin/bash

echo "run_setup"
function run_setup {
    avocado run src/SetUp.py --mux-yaml data/PA6/setup.yaml --execution-order=tests-per-variant
}

echo "run_collect"
function run_collect {
    avocado run src/Collect.py --mux-yaml data/PA6/collect.yaml --execution-order=tests-per-variant
}

echo "run_compare"
function run_compare {
    avocado run src/Compare.py --mux-yaml data/PA6/compare.yaml --execution-order=tests-per-variant
}

echo "avo_results"
function get_results {
    cat ~/avocado/job-results/latest/job.log
}


echo "get_variants"
function get_variants {
    avocado variants -m grade_pa6.py.data/grade_pa6.yaml --variants 2 --summary 2
}
