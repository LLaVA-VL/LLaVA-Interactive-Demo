import os
import httpx
import fire
import logging
from rich.logging import RichHandler


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


def main(
    imds_endpoint: str = os.environ.get('IMDS_ENDPOINT', 'http://localhost:40342'),
    identity_endpoint: str = os.environ.get(
        'IDENTITY_ENDPOINT', f'http://localhost:40342/metadata/identity/oauth2/token'
    ),
    proxy_port: int = 8000,
):
    logging.info(f'Start IMDS proxy service on port {proxy_port}...')
    logging.info(f"IMDS endpoint: {imds_endpoint}")
    logging.info(f"Identity endpoint: {identity_endpoint}")

    # Change to remove resource and see if still works
    management_resource_url = "https://management.azure.com"
    challenge_token = get_challenge_token(identity_endpoint, management_resource_url)
    management_access_token = get_access_token(identity_endpoint, challenge_token, management_resource_url)

    cognitive_service_resource_url = "https://cognitiveservices.azure.com"
    challenge_token = get_challenge_token(identity_endpoint, cognitive_service_resource_url)
    cognitive_service_access_token = get_access_token(
        identity_endpoint, challenge_token, cognitive_service_resource_url
    )


if __name__ == "__main__":
    format = '%(asctime)s | %(levelname)7s | %(name)s | %(message)s'
    # format="%(message)s"

    logging.basicConfig(
        level=os.environ.get("LOGLEVEL", "INFO").upper(),
        format=format,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=False)],
    )

    logger_blocklist = ["azure", "msal", "azureml", "urllib3", "msrest", "asyncio", "httpx"]
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)

    fire.Fire(main)
