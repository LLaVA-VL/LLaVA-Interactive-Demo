# Run the Demo using Docker

## Build Images

```bash
docker compose -f docker_demo/docker-compose.yaml up --build
```

## Inspect Containers

```bash
docker run --rm -it --entrypoint bash docker_demo-llava
```

## Manually build single container

```bash
docker build -t llava \
  -f ./docker_demo/llava/Dockerfile \
  .

docker run -it \
  -v .:/opt/llava \
  --gpus all \
  --entrypoint bash llava

docker inspect llava
```

## Test Docker Nvidia GPUs

```bash
docker build -t cuda-test -f docker_demo/cuda_test/Dockerfile .
```

```bash
docker run --gpus all nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04 nvidia-smi
```