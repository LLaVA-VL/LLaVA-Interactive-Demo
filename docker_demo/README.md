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
docker build -t llava -f ./docker_demo/llava/Dockerfile .
docker run -it -v .:/opt/llava --entrypoint bash llava
docker inspect llava
```

```bash
docker build -t lama -f ./docker_demo/lama/Dockerfile --progress=plain .
docker run -it -v .:/opt/lama --entrypoint bash lama
docker inspect lama
```
