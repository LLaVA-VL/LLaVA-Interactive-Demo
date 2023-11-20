#!/bin/bash

pkill -9 -f llava.serve.controller
pkill -9 -f llava.serve.model_worker
pkill -9 -f lama_server
pkill -9 -f llava_interactive

eval "$(conda shell.bash hook)"

# Check if --debug is in the command line arguments
if [[ " $* " == *" --debug "* ]]; then
  RUN_LLAVA_INT=False
else
  RUN_LLAVA_INT=True
fi

echo "RUN_LLAVA_INT: $RUN_LLAVA_INT"

# Test for environment variables
if [ -z "$GUARDLIST_KEY" ]; then
  echo "❗GUARDLIST_KEY environment variable must be set!"
  exit 1
fi

if [ -z "$CONTENT_SAFETY_KEY" ]; then
  echo "❗ CONTENT_SAFETY_KEY environment variable must be set!"
  exit 1
fi

(
cd LLaVA; \
pwd; \
conda deactivate; \
conda activate llava; \
export CONTROLLER_PORT=10000; \
export MODEL_WORKER_PORT=40000; \
python -m llava.serve.controller \
  --host 0.0.0.0 \
  --port $CONTROLLER_PORT & \
python -m llava.serve.model_worker \
  --host 0.0.0.0 \
  --controller http://localhost:$CONTROLLER_PORT \
  --port $MODEL_WORKER_PORT \
  --worker http://localhost:$MODEL_WORKER_PORT \
  --model-path ./llava-v1.5-13b &
)

sleep 30

(
conda deactivate; \
conda activate lama; \
cd lama; \
pwd; \
export TORCH_HOME=$(pwd) && export PYTHONPATH=$(pwd); \
python ../lama_server.py &
)

sleep 10

if [ "$RUN_LLAVA_INT" = "True" ]; then
  (
  pwd; \
  conda deactivate; \
  conda activate llava_int; \
  export LLAVA_INTERACTIVE_HOME=.; \
  python llava_interactive.py \
    --moderate \
    input_text_guardlist \
    input_text_aics \
    input_image_aics \
    output_text_guardlist \
    output_text_aics \
    gligen_input_text_guardlist \
    gligen_input_text_aics \
    gligen_output_image_aics
  )
else
  echo "Skipping llava_interactive.py because --debug was given."
fi
