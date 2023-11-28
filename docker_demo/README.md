# Run the Demo using Docker

## Build Images

```bash
docker compose -f docker_demo/docker-compose.yaml up --build
```

## Inspect Containers

```bash
docker compose -f docker_demo/docker-compose.yaml exec llava_interactive bash
```

## Manually build single container

```bash
docker build -t llava \
  -f ./docker_demo/llava/Dockerfile \
  .

docker run -it \
  -p 10001:10000 \
  -p 40001:40000 \
  -v .:/opt/app:rw \
  --gpus '"device=2,3"' \
  --name llava llava
```

```bash
source ~/miniconda3/bin/activate
conda activate llava

source .env.export
export PYTHONNET_RUNTIME=coreclr

pip install artifacts-keyring
pip install GuardlistPython==0.4.12 --index-url=https://office.pkgs.visualstudio.com/_packaging/Office/pypi/simple/

bash docker_demo/llava/start.sh
```

```bash
docker exec -it 4afbed1fce /bin/bash
```

## Test Docker Nvidia GPUs

```bash
docker run --gpus all nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 nvidia-smi
```
