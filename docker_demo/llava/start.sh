#! /bin/bash

set -e

CONTROLLER_PORT=10000
WORKER_PORT=40000

cd LLaVA

source ~/miniconda3/bin/activate
conda activate llava

python -m llava.serve.controller \
  --host 0.0.0.0 \
  --port $CONTROLLER_PORT & \
python -m llava.serve.model_worker \
  --host 0.0.0.0 \
  --controller http://localhost:$CONTROLLER_PORT \
  --port $WORKER_PORT \
  --worker http://localhost:$WORKER_PORT \
  --model-path ./llava-v1.5-13b