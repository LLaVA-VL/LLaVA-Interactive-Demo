import httpx
import logging
import os
from fastapi import FastAPI

app = FastAPI()


def get_challenge_token(imds_token_endpoint: str, resource_url: str) -> str:
    response = httpx.get(
        imds_token_endpoint,
        headers={"Metadata": "true"},
        params={"api-version": "2019-11-01", "resource": resource_url},
    )
    challenge_token_line = response.headers.get("Www-Authenticate")
    challenge_token_path = challenge_token_line.split("=")[1].strip()
    logging.info(f"Challenge token path: {challenge_token_path}")

    with open(challenge_token_path, "r") as file:
        challenge_token = file.read()

    if not challenge_token:
        logging.warn("Could not retrieve challenge token, double check that this command is run with root privileges.")
        exit(1)

    logging.info(f"Challenge token read: {challenge_token[:10]}...{challenge_token[-10:]}")
    return challenge_token


def get_access_token(imds_token_endpoint: str, challenge_token: str, resource_url: str) -> str:
    response = httpx.get(
        imds_token_endpoint,
        headers={"Metadata": "true", "Authorization": f"Basic {challenge_token}"},
        params={"api-version": "2019-11-01", "resource": resource_url},
    )
    response.raise_for_status()
    access_token = response.json().get("access_token")
    logging.info(f"Access token: {access_token[:10]}...{access_token[-10:]}")

    return access_token


@app.get("/")
def get_root():
    return "IMDS Proxy Service for Docker"


@app.get("/token")
def get_token(resource_url: str = "https://cognitiveservices.azure.com"):
    identity_endpoint = os.environ.get('IDENTITY_ENDPOINT', f'http://localhost:40342/metadata/identity/oauth2/token')
    challenge_token = get_challenge_token(identity_endpoint, resource_url)
    cognitive_service_access_token = get_access_token(identity_endpoint, challenge_token, resource_url)

    return {"access_token": cognitive_service_access_token, "resource_url": resource_url}
