import json
import os
import time
import httpx
from pathlib import Path

import fire
from azure.identity import DefaultAzureCredential, EnvironmentCredential, ManagedIdentityCredential
from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from azure.cognitiveservices.vision.contentmoderator.models import Evaluate, Screen

from .logger import get_logger

logger = get_logger(__name__)


def screen_text(
    text_file_path: str | Path,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
    num_requests: int = 1,
    interval_seconds: float = 0,
):
    """Given text file path, screen the text using Azure Content Moderation Service

    :param text_file_path: Path to text file
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]

    Example:

        ```bash
        python -m azure_content_moderator screen_text \
            --text_file_path azure_content_moderator/text_files/email01.txt
        ```
    """

    # credential = DefaultAzureCredential()
    # credential = EnvironmentCredential()
    credential = ManagedIdentityCredential()
    client = ContentModeratorClient(endpoint, credential)

    logger.info(f'Text Moderation: {text_file_path}')
    with open(text_file_path, "rb") as text_file:
        text_content = text_file.read().decode("utf-8")
        for i in range(num_requests):
            screen = client.text_moderation.screen_text(
                text_content_type="text/plain", text_content=text_file, language="eng", autocorrect=True, pii=True
            )
            assert isinstance(screen, Screen)
            logger.info(f'Reqest: {i+1:<2} Text Moderation: Screen Text Response')
            logger.info(json.dumps(screen.as_dict(), indent=2))

            time.sleep(interval_seconds)


def screen_text_rest(
    text_file_path: str | Path,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
    num_requests: int = 1,
    interval_seconds: float = 0,
):
    """Given text file path, screen the text using Azure Content Moderation Service

    :param text_file_path: Path to text file
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]

    Example:

        ```bash
        python -m azure_content_moderator screen_text_rest \
            --text_file_path azure_content_moderator/text_files/email01.txt
        ```
    """

    logger.info(f'Text Moderation: {text_file_path}')
    with open(text_file_path, "rb") as text_file:
        text_content = text_file.read().decode("utf-8")
        for i in range(num_requests):
            screen_dict = _screen_text_rest(input_text=text_content, endpoint=endpoint)
            screen = Screen.deserialize(screen_dict)
            assert isinstance(screen, Screen)
            logger.info(f'Reqest: {i+1:<2} Text Moderation: Screen Text Response')
            logger.info(json.dumps(screen.as_dict(), indent=2))

            time.sleep(interval_seconds)

def _screen_text_rest(
    input_text: str,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
):
    """Given text file path, screen the text using Azure Content Moderation Service

    :param text_file_path: Path to text file
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]
    """

    credential = DefaultAzureCredential()
    access_token = credential.get_token("https://cognitiveservices.azure.com/.default")

    # https://learn.microsoft.com/en-us/rest/api/cognitiveservices/contentmoderator/text-moderation/screen-text?view=rest-cognitiveservices-contentmoderator-v1.0&tabs=HTTP
    # Example from SDK: https://llava-int-contentmoderator.cognitiveservices.azure.com/contentmoderator/moderate/v1.0/ProcessText/Screen/?language=eng&autocorrect=true&PII=true&classify=false
    response = httpx.post(
        f"{endpoint}/contentmoderator/moderate/v1.0/ProcessText/Screen/?language=eng&autocorrect=true&PII=true&classify=false",
        headers={
            "Authorization": f"Bearer {access_token.token}",
            "Content-Type": "text/plain",
        },
        json=input_text,
    )

    response.raise_for_status()
    response_json = response.json()

    return response_json



def _screen_text_rest_imds(
    input_text: str,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
    imds_endpoint=os.environ["IDENTITY_ENDPOINT"],
):
    """Given text file path, screen the text using Azure Content Moderation Service

    :param text_file_path: Path to text file
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]
    """

    challenge_response = httpx.post(
        f"{imds_endpoint}?api-version=2019-11-01&resource=https%3A%2F%2Fmanagement.azure.com",
        headers={
            "Metadata": "true",
        },
    )

    challenge_response.raise_for_status()
    print(challenge_response)

    # https://learn.microsoft.com/en-us/rest/api/cognitiveservices/contentmoderator/text-moderation/screen-text?view=rest-cognitiveservices-contentmoderator-v1.0&tabs=HTTP
    # Example from SDK: https://llava-int-contentmoderator.cognitiveservices.azure.com/contentmoderator/moderate/v1.0/ProcessText/Screen/?language=eng&autocorrect=true&PII=true&classify=false
    response = httpx.post(
        f"{endpoint}/contentmoderator/moderate/v1.0/ProcessText/Screen/?language=eng&autocorrect=true&PII=true&classify=false",
        headers={
            "Authorization": f"Bearer {access_token.token}",
            "Content-Type": "text/plain",
        },
        json=input_text,
    )

    response.raise_for_status()
    response_json = response.json()

    return response_json


def screen_image(
    image_url: str,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
    num_requests: int = 1,
    interval_seconds: float = 0,
):
    """Given image url, screen the image using Azure Content Moderation Service

    :param image_url: Image URL
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]

    Example:

        ```bash
        python -m azure_content_moderator screen_image \
            --image_url https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/celebrities.jpg
        ```
    """

    credential = DefaultAzureCredential()
    client = ContentModeratorClient(endpoint, credential)

    for i in range(num_requests):
        logger.info(f"Request: {i+1:<2} Evaluate image {image_url}")

        evaluation = client.image_moderation.evaluate_url_input(
            content_type="application/json", cache_image=True, data_representation="URL", value=image_url
        )
        assert isinstance(evaluation, Evaluate)

        logger.info(f'Is Adult Content: {evaluation.is_image_adult_classified}')
        logger.info(f'Is Racy Content: {evaluation.is_image_racy_classified}')

        time.sleep(interval_seconds)


if __name__ == "__main__":
    fire.Fire()
