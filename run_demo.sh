#!/bin/bash

pkill -9 -f llava.serve.controller
pkill -9 -f llava.serve.model_worker
pkill -9 -f lama_server
pkill -9 -f llava_interactive

eval "$(conda shell.bash hook)"

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
conda deactivate; \
cd LLaVA; \
pwd; \
conda activate llava; \
python -m llava.serve.controller --host 0.0.0.0 --port 10000 & \
python -m llava.serve.model_worker --host 0.0.0.0 --controller http://localhost:10000 --port 40000 --worker http://localhost:40000 --model-path ./llava-v1.5-13b &
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

(
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
