import json
import os
import time
from pathlib import Path

import fire
from azure.identity import DefaultAzureCredential
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

    credential = DefaultAzureCredential()
    client = ContentModeratorClient(endpoint=endpoint, credentials=credential)

    logger.info(f'Text Moderation: {text_file_path}')
    with open(text_file_path, "rb") as text_fd:
        for i in range(num_requests):
            screen = client.text_moderation.screen_text(
                text_content_type="text/plain", text_content=text_fd, language="eng", autocorrect=True, pii=True
            )
            assert isinstance(screen, Screen)
            logger.info(f'Reqest: {i+1:<2} Text Moderation: Screen Text Response')
            logger.info(json.dumps(screen.as_dict(), indent=2))

            time.sleep(interval_seconds)


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
    client = ContentModeratorClient(endpoint=endpoint, credentials=credential)

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
