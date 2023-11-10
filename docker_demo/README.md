# Run the Demo using Docker

## Build Images

```bash
docker compose -f docker_demo/docker-compose.yaml up --build
```

## Inspect Containers

```bash
docker run --rm -it docker_demo-llava
```

## Manually build single container

```bash
docker build -t llava -f ./docker_demo/llava/Dockerfile .
docker run --rm -it -v .:/opt/llava --entrypoint bash llava
docker inspect llava
```
