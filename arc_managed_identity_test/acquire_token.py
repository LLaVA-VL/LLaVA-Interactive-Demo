import os
import httpx
import fire
import logging
from rich.logging import RichHandler


def get_challenge_token(imds_token_endpoint: str) -> str:
    response = httpx.get(imds_token_endpoint, headers={"Metadata": "true"})
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
    resource_url: str = "https://cognitiveservices.azure.com",
):
    logging.info(f'Start IMDS proxy service on port {proxy_port}...')
    management_endpoint = f"{identity_endpoint}?api-version=2019-11-01&resource=https%3A%2F%2Fmanagement.azure.com"
    logging.info(f"IMDS endpoint: {imds_endpoint}")
    logging.info(f"Identity endpoint: {identity_endpoint}")
    logging.info(f"Management endpoint: {management_endpoint}")

    # Change to remove resource and see if still works
    challenge_token = get_challenge_token(management_endpoint)
    management_resource_url = "https://management.azure.com"
    management_access_token = get_access_token(management_endpoint, challenge_token, management_resource_url)

    challenge_token = get_challenge_token(management_endpoint)
    cognitive_service_access_token = get_access_token(management_endpoint, challenge_token, resource_url)


if __name__ == "__main__":
    format='%(asctime)s | %(levelname)7s | %(name)s | %(message)s'
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
