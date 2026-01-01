#!/bin/bash

CUR_DIR=$(dirname "$(realpath $0)")
PROJECT_PATH=$(dirname "$CUR_DIR")
TEST_PATH=${PROJECT_PATH}/test
ARGS=$@

cd $TEST_PATH
python3 -m unittest discover  -v  -p "test_*.py"