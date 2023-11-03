import json
import os
from pathlib import Path

import fire
from azure.cognitiveservices.vision.contentmoderator import \
    ContentModeratorClient
from azure.cognitiveservices.vision.contentmoderator.models import (Evaluate,
                                                                    Screen)
from msrest.authentication import CognitiveServicesCredentials
from rich import print


def screen_text(
    text_file_path: str | Path,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
    key=os.environ["CONTENT_MODERATOR_KEY"]
):
    """Given text file path, screen the text using Azure Content Moderation Service

    :param text_file_path: Path to text file
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]
    :param key: Content Moderation Key, defaults to os.environ["CONTENT_MODERATOR_KEY"]

    Example:

        ```bash
        python -m azure_content_moderation screen_text \
            --text_file_path azure_content_moderator/text_files/email01.txt
        ```
    """

    client = ContentModeratorClient(
        endpoint=endpoint,
        credentials=CognitiveServicesCredentials(key)
    )

    print(f'Text Moderation: {text_file_path}')
    with open(text_file_path, "rb") as text_fd:
        screen = client.text_moderation.screen_text(
            text_content_type="text/plain",
            text_content=text_fd,
            language="eng",
            autocorrect=True,
            pii=True
        )
        assert isinstance(screen, Screen)
        print(f'Text Moderation: Screen Text Response')
        print(json.dumps(screen.as_dict(), indent=2))


def screen_image(
    image_url: str,
    endpoint=os.environ["CONTENT_MODERATOR_ENDPOINT"],
    key=os.environ["CONTENT_MODERATOR_KEY"]
):
    """Given image url, screen the image using Azure Content Moderation Service

    :param image_url: Image URL
    :param endpoint: Content Moderation Service Endpoint, defaults to os.environ["CONTENT_MODERATOR_ENDPOINT"]
    :param key: Content Moderation Key, defaults to os.environ["CONTENT_MODERATOR_KEY"]

    Example:

        ```bash
        python -m azure_content_moderator screen_image \
            --image_url https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/ComputerVision/Images/celebrities.jpg
        ```
    """

    client = ContentModeratorClient(
        endpoint=endpoint,
        credentials=CognitiveServicesCredentials(key)
    )

    print(f"Evaluate image {image_url}")

    evaluation = client.image_moderation.evaluate_url_input(
        content_type="application/json",
        cache_image=True,
        data_representation="URL",
        value=image_url
    )
    assert isinstance(evaluation, Evaluate)

    print(f'Is Adult Content: {evaluation.is_image_adult_classified}')
    print(f'Is Racy Content: {evaluation.is_image_racy_classified}')
    print(json.dumps(evaluation.as_dict(), indent=2))
    print()


if __name__ == "__main__":
    fire.Fire()
