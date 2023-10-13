#!/bin/bash

eval "$(conda shell.bash hook)"

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
conda activate c4c_env_test; \
export C4C_HOME=.; \
python app.py
)

