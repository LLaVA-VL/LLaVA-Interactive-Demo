#! /bin/bash

set -e

source ~/miniconda3/bin/activate
conda activate llava_int

export LLAVA_INTERACTIVE_HOME=.

python llava_interactive.py --controller-url http://localhost:10001
