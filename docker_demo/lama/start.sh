#! /bin/bash

set -e

source ~/miniconda3/bin/activate
conda activate lama

cd lama

export TORCH_HOME=$(pwd)
export PYTHONPATH=$(pwd)

python ../lama_server.py
