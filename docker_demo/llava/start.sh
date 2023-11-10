#! /bin/bash

set -ex

export TORCH_HOME=$(pwd)
export PYTHONPATH=$(pwd)

python ../lama_server.py
