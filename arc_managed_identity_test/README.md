# Acquiring tokens on GCR machine with Azure ARC - IMDS service

https://learn.microsoft.com/en-us/azure/azure-arc/servers/managed-identity-authentication


## Verification of IMDS

### Setup

```bash
export IMDS_ENDPOINT=http://host.docker.internal:40342
export IDENTITY_ENDPOINT="${IMDS_ENDPOINT}/metadata/identity/oauth2/token"
```

### Run Script

```bash
sudo -E bash ./arc_managed_identity_test/acquire_token.sh
```

## Host Setup

### Create conda environment

```
conda create -n imds_proxy -c conda-forge -c pytorch python=3.12 -y
conda activate imds_proxy

pip install -r requirements.txt
```
### Run Start IMDS Token Proxy Service

```bash
python -m arc_managed_identity_test.acquire_token
```

