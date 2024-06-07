# Acquiring tokens on GCR machine with Azure ARC - IMDS service

https://learn.microsoft.com/en-us/azure/azure-arc/servers/managed-identity-authentication


## Verification of IMDS (Bash)

### Setup

```bash
# export IMDS_ENDPOINT="http://host.docker.internal:8000"
export IMDS_ENDPOINT="http://localhost:40342"
export IDENTITY_ENDPOINT="${IMDS_ENDPOINT}/metadata/identity/oauth2/token"
```

### Run Script

```bash
sudo -E bash ./arc_managed_identity_test/acquire_token.sh
```

## Python Setup

### Create environment

```
conda create -n imds_proxy -c conda-forge -c pytorch python=3.12 -y
conda activate imds_proxy

pip install -r requirements.txt
```

### Run Acquire Token Script

```bash
sudo -E $(which python) -m arc_managed_identity_test.acquire_token
```

### Run Start IMDS Token Proxy Service

> Note: fastify dev binds to 127.0.0.1 which is only reachable by other localhosts
> Note: fastify run binds to 0.0.0.0 which is reachable by other hosts such as the container

```bash
sudo -E $(which fastapi) run arc_managed_identity_test/acquire_token_server.py
```

# Other

## Running Redirect Server

```bash
python -m arc_managed_identity_test.imds_proxy_service
```
